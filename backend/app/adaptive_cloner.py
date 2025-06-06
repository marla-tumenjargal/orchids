# adaptive_cloner.py - NEW FILE: Add this to your project
import re
from typing import Dict, List, Any, Tuple

class AdaptiveWebsiteAnalyzer:
    """Analyzes website type and adapts generation strategy accordingly"""
    
    def __init__(self):
        self.website_patterns = {
            'blog': {
                'indicators': ['blog', 'post', 'article', 'wordpress', 'medium'],
                'content_structure': ['h1', 'h2', 'article', 'time', 'author'],
                'layout_type': 'content_focused'
            },
            'ecommerce': {
                'indicators': ['shop', 'cart', 'product', 'price', 'buy', 'checkout'],
                'content_structure': ['product', 'grid', 'filter', 'category'],
                'layout_type': 'grid_focused'
            },
            'portfolio': {
                'indicators': ['portfolio', 'gallery', 'work', 'project', 'design'],
                'content_structure': ['gallery', 'grid', 'masonry', 'lightbox'],
                'layout_type': 'visual_focused'
            },
            'saas': {
                'indicators': ['pricing', 'features', 'dashboard', 'login', 'signup'],
                'content_structure': ['hero', 'features', 'pricing', 'cta'],
                'layout_type': 'conversion_focused'
            },
            'social': {
                'indicators': ['profile', 'feed', 'follow', 'share', 'like', 'post'],
                'content_structure': ['feed', 'timeline', 'card', 'infinite-scroll'],
                'layout_type': 'feed_focused'
            },
            'productivity': {
                'indicators': ['workspace', 'notes', 'todo', 'task', 'organize'],
                'content_structure': ['sidebar', 'canvas', 'toolbar', 'panel'],
                'layout_type': 'tool_focused'
            },
            'news': {
                'indicators': ['news', 'breaking', 'headline', 'story', 'journalist'],
                'content_structure': ['headline', 'byline', 'lead', 'section'],
                'layout_type': 'content_hierarchy'
            }
        }
    
    def detect_website_type(self, scraped_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect website type based on content, structure, and patterns"""
        
        # Extract analysis data
        url = scraped_data.get('url', '').lower()
        title = scraped_data.get('title', '').lower()
        text_content = scraped_data.get('text_content', '').lower()
        headings = scraped_data.get('structure', {}).get('headings', [])
        navigation = scraped_data.get('navigation', {})
        images = scraped_data.get('images', [])
        forms = scraped_data.get('forms', [])
        
        # Calculate scores for each website type
        type_scores = {}
        
        for website_type, patterns in self.website_patterns.items():
            score = 0
            
            # Check URL indicators
            for indicator in patterns['indicators']:
                if indicator in url:
                    score += 15
                if indicator in title:
                    score += 10
                if indicator in text_content:
                    score += 5
            
            # Check content structure
            score += self._analyze_content_structure(scraped_data, patterns['content_structure'])
            
            # Check layout patterns
            score += self._analyze_layout_patterns(scraped_data, patterns['layout_type'])
            
            type_scores[website_type] = score
        
        # Determine primary and secondary types
        sorted_types = sorted(type_scores.items(), key=lambda x: x[1], reverse=True)
        
        primary_type = sorted_types[0][0] if sorted_types[0][1] > 20 else 'generic'
        secondary_type = sorted_types[1][0] if len(sorted_types) > 1 and sorted_types[1][1] > 15 else None
        
        # Detailed feature detection
        features = self._detect_specific_features(scraped_data, primary_type)
        
        return {
            'primary_type': primary_type,
            'secondary_type': secondary_type,
            'confidence': min(sorted_types[0][1] / 100, 1.0) if sorted_types else 0,
            'type_scores': type_scores,
            'detected_features': features,
            'layout_strategy': self.website_patterns.get(primary_type, {}).get('layout_type', 'generic'),
            'specialized_components': self._get_specialized_components(primary_type, features)
        }
    
    def _analyze_content_structure(self, scraped_data: Dict, expected_structure: List[str]) -> int:
        """Analyze if content matches expected structure patterns"""
        score = 0
        
        # Check semantic elements
        semantic_elements = scraped_data.get('structure', {}).get('semantic_elements', [])
        semantic_tags = [el.get('tag') for el in semantic_elements]
        
        for expected in expected_structure:
            if expected in semantic_tags:
                score += 8
            
            # Check in class names and IDs
            for element in semantic_elements:
                classes = ' '.join(element.get('class', []))
                if expected in classes.lower():
                    score += 5
        
        return score
    
    def _analyze_layout_patterns(self, scraped_data: Dict, layout_type: str) -> int:
        """Analyze layout patterns specific to website type"""
        score = 0
        layout_data = scraped_data.get('layout', {})
        containers = layout_data.get('containers', [])
        
        if layout_type == 'grid_focused':
            # Look for grid layouts
            for container in containers:
                styles = container.get('styles', {})
                if 'grid' in styles.get('display', ''):
                    score += 15
                if 'flex' in styles.get('display', ''):
                    score += 10
        
        elif layout_type == 'content_focused':
            # Look for content-focused layouts
            for container in containers:
                styles = container.get('styles', {})
                # Check for reading-optimized widths
                position = container.get('position', {})
                width = position.get('width', 0)
                if 600 <= width <= 1000:  # Typical content width
                    score += 12
        
        elif layout_type == 'feed_focused':
            # Look for feed/timeline layouts
            for container in containers:
                class_name = container.get('className', '').lower()
                if any(term in class_name for term in ['feed', 'timeline', 'stream', 'list']):
                    score += 15
        
        elif layout_type == 'tool_focused':
            # Look for application-like layouts
            for container in containers:
                styles = container.get('styles', {})
                position = container.get('position', {})
                if styles.get('position') == 'fixed' or position.get('width', 0) < 300:
                    score += 10  # Likely sidebar
        
        return score
    
    def _detect_specific_features(self, scraped_data: Dict, website_type: str) -> List[str]:
        """Detect specific features based on website type"""
        features = []
        
        # Common feature detection
        if scraped_data.get('forms'):
            features.append('forms')
        
        if len(scraped_data.get('images', [])) > 10:
            features.append('image_heavy')
        
        if scraped_data.get('computed_styles', {}).get('computedColors'):
            features.append('interactive')
        
        # Type-specific feature detection
        if website_type == 'ecommerce':
            text_content = scraped_data.get('text_content', '').lower()
            if "'" in text_content or "€" in text_content or "price" in text_content:
                features.append('pricing')
            if 'cart' in text_content or 'add to' in text_content:
                features.append('shopping_cart')
        
        elif website_type == 'social':
            if 'follow' in scraped_data.get('text_content', '').lower():
                features.append('social_interactions')
            if len(scraped_data.get('images', [])) > 5:
                features.append('media_sharing')
        
        elif website_type == 'productivity':
            nav_elements = scraped_data.get('navigation', {}).get('navElements', [])
            for nav in nav_elements:
                links = nav.get('links', [])
                link_texts = [link.get('text', '').lower() for link in links]
                if any(term in ' '.join(link_texts) for term in ['workspace', 'docs', 'team', 'settings']):
                    features.append('workspace_navigation')
        
        elif website_type == 'portfolio':
            if len(scraped_data.get('images', [])) > 8:
                features.append('gallery')
            headings = scraped_data.get('structure', {}).get('headings', [])
            heading_texts = [h.get('text', '').lower() for h in headings]
            if any(term in ' '.join(heading_texts) for term in ['project', 'work', 'case study']):
                features.append('project_showcase')
        
        return features
    
    def _get_specialized_components(self, website_type: str, features: List[str]) -> List[str]:
        """Get specialized components needed for this website type"""
        components = []
        
        if website_type == 'ecommerce':
            components.extend(['product-grid', 'product-card', 'filter-sidebar'])
            if 'shopping_cart' in features:
                components.append('cart-icon')
            if 'pricing' in features:
                components.append('price-display')
        
        elif website_type == 'social':
            components.extend(['post-card', 'user-profile', 'interaction-buttons'])
            if 'media_sharing' in features:
                components.extend(['image-gallery', 'media-upload'])
        
        elif website_type == 'productivity':
            components.extend(['sidebar-navigation', 'main-canvas', 'toolbar'])
            if 'workspace_navigation' in features:
                components.append('workspace-switcher')
        
        elif website_type == 'portfolio':
            components.extend(['hero-section', 'project-grid'])
            if 'gallery' in features:
                components.append('lightbox-gallery')
            if 'project_showcase' in features:
                components.append('case-study-layout')
        
        elif website_type == 'blog':
            components.extend(['article-layout', 'sidebar', 'comment-section'])
        
        elif website_type == 'saas':
            components.extend(['hero-section', 'feature-grid', 'pricing-table', 'cta-section'])
        
        return components

def create_adaptive_code_generation_prompt(scraped_data: Dict[str, Any], analysis: str, original_url: str, website_analysis: Dict[str, Any]) -> str:
    """Create specialized code generation prompt based on website type"""
    
    website_type = website_analysis['primary_type']
    features = website_analysis['detected_features']
    components = website_analysis['specialized_components']
    
    # Base prompt with actual content
    actual_title = scraped_data.get('title', 'Website Clone')
    actual_headings = scraped_data.get('structure', {}).get('headings', [])
    actual_nav = scraped_data.get('navigation', {})
    actual_images = scraped_data.get('images', [])
    
    prompt = f"""You are creating a pixel-perfect clone of a {website_type.upper()} website. 
This requires specialized components and layouts specific to {website_type} websites.

=== WEBSITE TYPE: {website_type.upper()} ===
Primary Type: {website_type}
Secondary Type: {website_analysis.get('secondary_type', 'None')}
Confidence: {website_analysis['confidence']*100:.1f}%
Layout Strategy: {website_analysis['layout_strategy']}

=== DETECTED FEATURES ===
{', '.join(features)}

=== REQUIRED SPECIALIZED COMPONENTS ===
{', '.join(components)}

=== ORIGINAL WEBSITE DATA ===
URL: {original_url}
Title: {actual_title}

=== ANALYSIS RESULTS ===
{analysis}

=== TYPE-SPECIFIC REQUIREMENTS ===
"""
    
    # Add type-specific requirements
    if website_type == 'ecommerce':
        prompt += """
**E-COMMERCE SPECIFIC REQUIREMENTS:**
- Product grid layout with cards
- Hover effects on product images
- Price display formatting
- Add to cart buttons
- Filter/search functionality UI
- Shopping cart icon in header
- Product image galleries
- Customer reviews sections
        """
        
    elif website_type == 'social':
        prompt += """
**SOCIAL MEDIA SPECIFIC REQUIREMENTS:**
- Feed/timeline layout
- Post cards with user avatars
- Like, share, comment buttons
- Profile sections
- Follow/unfollow buttons
- Image/media galleries
- Infinite scroll design
- User interaction elements
        """
        
    elif website_type == 'productivity':
        prompt += """
**PRODUCTIVITY APP SPECIFIC REQUIREMENTS:**
- Application-like layout with sidebars
- Main workspace/canvas area
- Toolbar with action buttons
- Collapsible navigation panels
- Settings/preferences UI
- Multi-panel layouts
- Drag and drop interfaces
- Modal dialogs and popups
        """
        
    elif website_type == 'portfolio':
        prompt += """
**PORTFOLIO SPECIFIC REQUIREMENTS:**
- Visual-first design with large images
- Project showcase grids
- Lightbox image galleries
- Case study layouts
- About section with bio
- Contact forms
- Smooth scrolling sections
- Image hover effects
        """
        
    elif website_type == 'blog':
        prompt += """
**BLOG SPECIFIC REQUIREMENTS:**
- Article-focused layout
- Reading-optimized typography
- Sidebar with widgets
- Tag and category systems
- Comment sections
- Author bio sections
- Related posts
- Archive/pagination
        """
        
    elif website_type == 'saas':
        prompt += """
**SAAS SPECIFIC REQUIREMENTS:**
- Conversion-focused hero section
- Feature benefit grids
- Pricing tables with tiers
- Strong call-to-action buttons
- Testimonial sections
- FAQ sections
- Demo/trial signup forms
- Trust signals and logos
        """
    
    # Add actual content extraction
    prompt += f"""

=== EXACT CONTENT TO RECREATE ===
**Title:** {actual_title}
**Headings:** {[h.get('text', '') for h in actual_headings[:10]]}
**Navigation:** {extract_nav_structure(actual_nav)}
**Images:** {len(actual_images)} images to recreate
**Key Content:** {scraped_data.get('text_content', '')[:500]}...

=== STYLING REQUIREMENTS ===
Colors: {scraped_data.get('computed_styles', {}).get('computedColors', [])[:8]}
Fonts: {scraped_data.get('fonts', [])[:3]}
Layout Containers: {len(scraped_data.get('layout', {}).get('containers', []))}

=== CODE GENERATION INSTRUCTIONS ===
1. Create HTML structure optimized for {website_type} websites
2. Include ALL detected specialized components: {', '.join(components)}
3. Use the EXACT content from the original website
4. Apply {website_type}-specific styling patterns
5. Ensure responsive design appropriate for {website_type} users
6. Include interactive elements typical of {website_type} sites

Generate complete, functional code that creates a perfect {website_type} website clone.
"""
    
    return prompt

def extract_nav_structure(navigation_data: Dict) -> List[str]:
    """Extract navigation structure for prompt"""
    nav_elements = navigation_data.get('navElements', [])
    nav_links = []
    
    for nav in nav_elements[:2]:  # First 2 nav elements
        links = nav.get('links', [])
        for link in links[:8]:  # First 8 links
            text = link.get('text', '').strip()
            if text:
                nav_links.append(text)
    
    return nav_links