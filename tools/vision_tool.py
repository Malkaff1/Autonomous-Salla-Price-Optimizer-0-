"""
Vision analysis tools for product image processing and price extraction.
This tool can analyze product images to extract pricing information and validate products.
"""

import os
import base64
import requests
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from crewai.tools import tool
from openai import OpenAI

logger = logging.getLogger(__name__)

@dataclass
class ProductImageAnalysis:
    """Data class for product image analysis results."""
    product_detected: bool
    product_name: str
    price_detected: bool
    extracted_price: Optional[float]
    currency: str
    confidence_score: float
    description: str
    brand: Optional[str] = None
    category: Optional[str] = None

class VisionAnalyzer:
    """Advanced vision analysis for e-commerce product images."""
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def analyze_product_image(self, image_url: str, expected_product: str = None) -> ProductImageAnalysis:
        """
        Analyze a product image to extract pricing and product information.
        
        Args:
            image_url: URL of the product image
            expected_product: Expected product name for validation
            
        Returns:
            ProductImageAnalysis object with extracted information
        """
        try:
            # Download and encode image
            image_data = self._download_image(image_url)
            if not image_data:
                return self._create_empty_analysis("Failed to download image")
            
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
            # Analyze with GPT-4 Vision
            analysis_result = self._analyze_with_gpt4_vision(base64_image, expected_product)
            
            return self._parse_vision_response(analysis_result)
            
        except Exception as e:
            logger.error(f"Vision analysis failed: {str(e)}")
            return self._create_empty_analysis(f"Analysis error: {str(e)}")
    
    def validate_product_match(self, image_url: str, product_name: str) -> Dict[str, Any]:
        """
        Validate if an image matches the expected product.
        
        Args:
            image_url: URL of the product image
            product_name: Expected product name
            
        Returns:
            Dictionary with validation results
        """
        analysis = self.analyze_product_image(image_url, product_name)
        
        # Calculate match score
        match_score = self._calculate_match_score(analysis.product_name, product_name)
        
        return {
            "is_match": match_score > 0.7,
            "match_score": match_score,
            "detected_product": analysis.product_name,
            "expected_product": product_name,
            "confidence": analysis.confidence_score,
            "reasoning": analysis.description
        }
    
    def extract_price_from_screenshot(self, image_url: str) -> Dict[str, Any]:
        """
        Extract price information from a product page screenshot.
        
        Args:
            image_url: URL of the screenshot image
            
        Returns:
            Dictionary with extracted price information
        """
        analysis = self.analyze_product_image(image_url)
        
        return {
            "price_found": analysis.price_detected,
            "extracted_price": analysis.extracted_price,
            "currency": analysis.currency,
            "confidence": analysis.confidence_score,
            "product_info": {
                "name": analysis.product_name,
                "brand": analysis.brand,
                "category": analysis.category
            }
        }
    
    def _download_image(self, image_url: str) -> Optional[bytes]:
        """Download image from URL."""
        try:
            response = requests.get(image_url, timeout=30, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.raise_for_status()
            return response.content
        except Exception as e:
            logger.error(f"Failed to download image from {image_url}: {str(e)}")
            return None
    
    def _analyze_with_gpt4_vision(self, base64_image: str, expected_product: str = None) -> str:
        """Analyze image using GPT-4 Vision."""
        system_prompt = """You are an expert e-commerce product analyst. Analyze the provided image and extract:

1. Product identification (name, brand, model)
2. Price information (amount, currency)
3. Product category
4. Quality assessment
5. Match validation (if expected product is provided)

Focus on Saudi Arabian e-commerce context. Look for Arabic text and SAR currency.
Provide detailed, accurate analysis in JSON format."""

        user_prompt = f"""Analyze this product image and provide detailed information:

Required analysis:
- Product name and brand
- Price (look for ر.س, SAR, ريال)
- Product category
- Image quality and clarity
- Confidence level (0-1)

{f"Expected product: {expected_product}" if expected_product else ""}

Return response in this JSON format:
{{
    "product_detected": true/false,
    "product_name": "detected product name",
    "brand": "brand name or null",
    "category": "product category",
    "price_detected": true/false,
    "extracted_price": price_number_or_null,
    "currency": "SAR/USD/etc",
    "confidence_score": 0.0-1.0,
    "description": "detailed analysis description",
    "quality_assessment": "image quality notes"
}}"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": user_prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                            }
                        ]
                    }
                ],
                max_tokens=1000,
                temperature=0.1
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"GPT-4 Vision analysis failed: {str(e)}")
            raise
    
    def _parse_vision_response(self, response: str) -> ProductImageAnalysis:
        """Parse GPT-4 Vision response into structured data."""
        try:
            import json
            
            # Try to extract JSON from response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx:end_idx]
                data = json.loads(json_str)
                
                return ProductImageAnalysis(
                    product_detected=data.get('product_detected', False),
                    product_name=data.get('product_name', ''),
                    price_detected=data.get('price_detected', False),
                    extracted_price=data.get('extracted_price'),
                    currency=data.get('currency', 'SAR'),
                    confidence_score=data.get('confidence_score', 0.0),
                    description=data.get('description', ''),
                    brand=data.get('brand'),
                    category=data.get('category')
                )
            else:
                raise ValueError("No valid JSON found in response")
                
        except Exception as e:
            logger.error(f"Failed to parse vision response: {str(e)}")
            return self._create_empty_analysis(f"Parse error: {str(e)}")
    
    def _calculate_match_score(self, detected: str, expected: str) -> float:
        """Calculate similarity score between detected and expected product names."""
        if not detected or not expected:
            return 0.0
        
        detected_lower = detected.lower()
        expected_lower = expected.lower()
        
        # Simple word overlap scoring
        detected_words = set(detected_lower.split())
        expected_words = set(expected_lower.split())
        
        if not expected_words:
            return 0.0
        
        overlap = len(detected_words.intersection(expected_words))
        return overlap / len(expected_words)
    
    def _create_empty_analysis(self, error_message: str) -> ProductImageAnalysis:
        """Create empty analysis result with error message."""
        return ProductImageAnalysis(
            product_detected=False,
            product_name="",
            price_detected=False,
            extracted_price=None,
            currency="SAR",
            confidence_score=0.0,
            description=error_message
        )

# CrewAI tool wrappers
@tool("analyze_product_image")
def analyze_product_image(image_url: str, expected_product: str = None) -> Dict[str, Any]:
    """
    Analyze a product image to extract pricing and product information.
    
    Args:
        image_url: URL of the product image to analyze
        expected_product: Optional expected product name for validation
        
    Returns:
        Dictionary with analysis results
    """
    try:
        analyzer = VisionAnalyzer()
        analysis = analyzer.analyze_product_image(image_url, expected_product)
        
        return {
            "product_detected": analysis.product_detected,
            "product_name": analysis.product_name,
            "brand": analysis.brand,
            "category": analysis.category,
            "price_detected": analysis.price_detected,
            "extracted_price": analysis.extracted_price,
            "currency": analysis.currency,
            "confidence_score": analysis.confidence_score,
            "description": analysis.description
        }
        
    except Exception as e:
        logger.error(f"Product image analysis failed: {str(e)}")
        return {
            "product_detected": False,
            "error": str(e)
        }

@tool("validate_product_image")
def validate_product_image(image_url: str, product_name: str) -> Dict[str, Any]:
    """
    Validate if a product image matches the expected product.
    
    Args:
        image_url: URL of the product image
        product_name: Expected product name
        
    Returns:
        Dictionary with validation results
    """
    try:
        analyzer = VisionAnalyzer()
        return analyzer.validate_product_match(image_url, product_name)
        
    except Exception as e:
        logger.error(f"Product image validation failed: {str(e)}")
        return {
            "is_match": False,
            "error": str(e)
        }

@tool("extract_price_from_screenshot")
def extract_price_from_screenshot(image_url: str) -> Dict[str, Any]:
    """
    Extract price information from a product page screenshot.
    
    Args:
        image_url: URL of the screenshot image
        
    Returns:
        Dictionary with extracted price information
    """
    try:
        analyzer = VisionAnalyzer()
        return analyzer.extract_price_from_screenshot(image_url)
        
    except Exception as e:
        logger.error(f"Price extraction from screenshot failed: {str(e)}")
        return {
            "price_found": False,
            "error": str(e)
        }

# Example usage
if __name__ == "__main__":
    # Test the vision analysis functionality
    analyzer = VisionAnalyzer()
    
    # Example image URL (replace with actual product image)
    test_image_url = "https://example.com/product-image.jpg"
    
    print("Testing vision analysis...")
    result = analyzer.analyze_product_image(test_image_url, "iPhone 15 Pro")
    print(f"Analysis result: {result}")