"""
Advanced market search tools for competitor analysis in the Saudi e-commerce market.
"""

import os
import requests
import time
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass
from crewai.tools import tool
from tavily import TavilyClient

logger = logging.getLogger(__name__)

@dataclass
class CompetitorResult:
    """Data class for competitor search results."""
    store_name: str
    product_name: str
    price: float
    url: str
    currency: str = "SAR"
    is_valid: bool = True
    confidence_score: float = 0.0

class SaudiMarketSearcher:
    """Advanced search functionality for Saudi e-commerce market."""
    
    def __init__(self):
        self.tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        self.target_domains = [
            "noon.com",
            "souq.com", 
            "amazon.sa",
            "jarir.com",
            "extra.com",
            "lulu.com",
            "carrefour.com",
            "danube.com.sa"
        ]
    
    def search_competitors(self, product_name: str, max_results: int = 10) -> List[CompetitorResult]:
        """
        Search for competitor prices across Saudi e-commerce platforms.
        
        Args:
            product_name: Name of the product to search for
            max_results: Maximum number of results to return
            
        Returns:
            List of CompetitorResult objects
        """
        results = []
        
        # Generate search queries for different platforms
        search_queries = self._generate_search_queries(product_name)
        
        for query in search_queries[:5]:  # Limit to 5 queries to avoid rate limits
            try:
                time.sleep(1)  # Rate limiting
                search_results = self.tavily_client.search(
                    query=query,
                    search_depth="advanced",
                    max_results=5,
                    include_domains=self.target_domains
                )
                
                for result in search_results.get('results', []):
                    competitor_result = self._parse_search_result(result, product_name)
                    if competitor_result and competitor_result.is_valid:
                        results.append(competitor_result)
                        
            except Exception as e:
                logger.error(f"Search failed for query '{query}': {str(e)}")
                continue
        
        # Sort by confidence score and return top results
        results.sort(key=lambda x: x.confidence_score, reverse=True)
        return results[:max_results]
    
    def _generate_search_queries(self, product_name: str) -> List[str]:
        """Generate optimized search queries for Saudi market."""
        base_queries = [
            f"{product_name} سعر السعودية",
            f"{product_name} price Saudi Arabia",
            f"شراء {product_name} السعودية",
            f"buy {product_name} KSA",
            f"{product_name} noon jarir extra"
        ]
        
        # Add brand-specific queries if product contains brand names
        common_brands = ["Samsung", "Apple", "Sony", "LG", "HP", "Dell", "Lenovo"]
        for brand in common_brands:
            if brand.lower() in product_name.lower():
                base_queries.append(f"{brand} {product_name} السعودية")
        
        return base_queries
    
    def _parse_search_result(self, result: Dict, product_name: str) -> Optional[CompetitorResult]:
        """Parse a search result and extract competitor information."""
        try:
            url = result.get('url', '')
            title = result.get('title', '')
            content = result.get('content', '')
            
            # Extract store name from URL
            store_name = self._extract_store_name(url)
            if not store_name:
                return None
            
            # Try to extract price from title and content
            price = self._extract_price(title + " " + content)
            if not price:
                return None
            
            # Calculate confidence score
            confidence = self._calculate_confidence(title, content, product_name, url)
            
            return CompetitorResult(
                store_name=store_name,
                product_name=title,
                price=price,
                url=url,
                confidence_score=confidence,
                is_valid=confidence > 0.3  # Minimum confidence threshold
            )
            
        except Exception as e:
            logger.error(f"Failed to parse search result: {str(e)}")
            return None
    
    def _extract_store_name(self, url: str) -> Optional[str]:
        """Extract store name from URL."""
        domain_mapping = {
            "noon.com": "Noon",
            "souq.com": "Souq",
            "amazon.sa": "Amazon KSA",
            "jarir.com": "Jarir",
            "extra.com": "eXtra",
            "lulu.com": "Lulu",
            "carrefour.com": "Carrefour",
            "danube.com.sa": "Danube"
        }
        
        for domain, name in domain_mapping.items():
            if domain in url.lower():
                return name
        
        return None
    
    def _extract_price(self, text: str) -> Optional[float]:
        """Extract price from text using regex patterns."""
        import re
        
        # Saudi Riyal patterns
        sar_patterns = [
            r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:ر\.س|SAR|riyal)',
            r'(?:ر\.س|SAR)\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
            r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*ريال',
            r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*SR'
        ]
        
        for pattern in sar_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    # Clean and convert to float
                    price_str = matches[0].replace(',', '')
                    price = float(price_str)
                    
                    # Validate price range (1 SAR to 50,000 SAR)
                    if 1 <= price <= 50000:
                        return price
                except ValueError:
                    continue
        
        return None
    
    def _calculate_confidence(self, title: str, content: str, product_name: str, url: str) -> float:
        """Calculate confidence score for the search result."""
        score = 0.0
        
        # Check if product name appears in title
        if product_name.lower() in title.lower():
            score += 0.4
        
        # Check if it's from a trusted domain
        trusted_domains = ["noon.com", "jarir.com", "extra.com", "amazon.sa"]
        if any(domain in url.lower() for domain in trusted_domains):
            score += 0.3
        
        # Check for price indicators
        price_indicators = ["ر.س", "SAR", "ريال", "price", "سعر"]
        if any(indicator in (title + content).lower() for indicator in price_indicators):
            score += 0.2
        
        # Check for product page indicators
        product_indicators = ["buy", "شراء", "product", "منتج", "/p/", "/product/"]
        if any(indicator in (title + url).lower() for indicator in product_indicators):
            score += 0.1
        
        return min(score, 1.0)

# CrewAI tool wrapper
@tool("advanced_market_search")
def advanced_market_search(product_name: str, max_results: int = 10) -> List[Dict]:
    """
    Advanced market search tool for finding competitor prices in Saudi Arabia.
    
    Args:
        product_name: Name of the product to search for
        max_results: Maximum number of results to return
        
    Returns:
        List of dictionaries containing competitor information
    """
    try:
        searcher = SaudiMarketSearcher()
        results = searcher.search_competitors(product_name, max_results)
        
        # Convert to dictionaries for JSON serialization
        return [
            {
                "store_name": result.store_name,
                "product_name": result.product_name,
                "price": result.price,
                "url": result.url,
                "currency": result.currency,
                "confidence_score": result.confidence_score,
                "is_valid": result.is_valid
            }
            for result in results
        ]
        
    except Exception as e:
        logger.error(f"Advanced market search failed: {str(e)}")
        return []

# Fashion-focused search tool
@tool("fashion_market_search")
def fashion_market_search(product_name: str, category: str = "fashion") -> List[Dict]:
    """
    Search for fashion product prices across Saudi Arabian fashion retailers.
    Optimized for women's fashion items with Arabic search terms.
    """
    
    # Fashion-specific retailers in Saudi Arabia
    fashion_domains = [
        "namshi.com",
        "styli.com", 
        "hm.com",
        "zara.com",
        "centrepointstore.com",
        "maxfashion.com",
        "splash.com",
        "redtag.com.sa",
        "nisnass.com",
        "ounass.com",
        "shein.com",
        "modanisa.com"
    ]
    
    # Enhanced Arabic search terms for fashion
    fashion_terms = {
        "dress": "فستان",
        "jacket": "جاكيت", 
        "abaya": "عباية",
        "hijab": "حجاب",
        "shoes": "حذاء",
        "bag": "حقيبة",
        "blouse": "بلوزة",
        "skirt": "تنورة",
        "pants": "بنطلون",
        "top": "توب",
        "coat": "معطف",
        "shirt": "قميص",
        "jeans": "جينز"
    }
    
    try:
        searcher = SaudiMarketSearcher()
        # Override target domains for fashion search
        searcher.target_domains = fashion_domains
        
        # Generate fashion-specific search queries
        search_queries = []
        
        # Add Arabic equivalent if available
        arabic_term = ""
        for eng_term, arabic in fashion_terms.items():
            if eng_term.lower() in product_name.lower():
                arabic_term = arabic
                break
        
        # Fashion-specific queries
        if arabic_term:
            search_queries.extend([
                f"{product_name} {arabic_term} السعودية",
                f"{arabic_term} موضة نساء السعودية",
                f"{product_name} fashion Saudi Arabia"
            ])
        else:
            search_queries.extend([
                f"{product_name} موضة نساء السعودية",
                f"{product_name} fashion women Saudi Arabia",
                f"{product_name} ملابس نسائية"
            ])
        
        # Add brand-specific queries
        fashion_brands = ["Zara", "H&M", "Mango", "Stradivarius", "Bershka", "Pull&Bear"]
        for brand in fashion_brands:
            if brand.lower() in product_name.lower():
                search_queries.append(f"{brand} {product_name} السعودية")
        
        all_results = []
        
        for query in search_queries[:4]:  # Limit queries
            try:
                time.sleep(1)  # Rate limiting
                search_results = searcher.tavily_client.search(
                    query=query,
                    search_depth="advanced", 
                    max_results=5,
                    include_domains=fashion_domains
                )
                
                for result in search_results.get('results', []):
                    competitor_result = searcher._parse_search_result(result, product_name)
                    if competitor_result and competitor_result.is_valid:
                        all_results.append({
                            "store_name": competitor_result.store_name,
                            "product_name": competitor_result.product_name,
                            "price": competitor_result.price,
                            "url": competitor_result.url,
                            "currency": competitor_result.currency,
                            "confidence_score": competitor_result.confidence_score,
                            "is_fashion_retailer": True,
                            "category": category
                        })
                        
            except Exception as e:
                logger.error(f"Fashion search failed for query '{query}': {str(e)}")
                continue
        
        # Sort by confidence and return top results
        all_results.sort(key=lambda x: x['confidence_score'], reverse=True)
        logger.info(f"✅ Found {len(all_results)} fashion competitor results")
        
        return all_results[:10]  # Top 10 results
        
    except Exception as e:
        logger.error(f"Fashion market search failed: {str(e)}")
        return []