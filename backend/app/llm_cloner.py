# llm_cloner.py - Updated to work better with Browserbase data
import os
from typing import Dict, Any, List, Optional, Callable
import json
from dotenv import load_dotenv
import logging
from anthropic import Anthropic
from .utils import measure_performance, retry_async, setup_logging

load_dotenv()
logger = logging.getLogger(__name__)

class LLMWebsiteCloner:
    
    def __init__(self):
        # Initialize Anthropic client
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        
        self.client = Anthropic(api_key=api_key)
        self.model = "claude-3-5-sonnet-20241022"
    
    @retry_async(max_retries=2)
    @measure_performance
    async def clone_website(self, scraped_data: Dict[str, Any], original_url: str) -> Dict[str, Any]:
        """
        Use AI to generate a clone of the website based on scraped data from Browserbase
        """
        logger.info(f"Starting AI cloning process for {original_url}")
        
        try:
            # Prepare enhanced context with Browserbase data
            analysis_prompt = self._create_enhanced_analysis_prompt(scraped_data, original_url)
            
            # Get AI analysis and recommendations
            analysis = await self._get_ai_analysis(analysis_prompt)
            
            # Generate HTML/CSS/JS code with enhanced context
            code_generation_prompt = self._create_enhanced_code_generation_prompt(scraped_data, analysis)
            generated_code = await self._generate_code(code_generation_prompt)
            
            # Create the final result with Browserbase metadata
            result = {
                'original_url': original_url,
                'analysis': analysis,
                'generated_code': generated_code,
                'clone_metadata': {
                    'title': scraped_data.get('title', 'Cloned Website'),
                    'description': scraped_data.get('meta_description', ''),
                    'generation_timestamp': self._get_timestamp(),
                    'total_elements_analyzed': self._count_elements(scraped_data),
                    'ai_model_used': self.model,
                    'browserbase_used': scraped_data.get('browserbase_used', False),
                    'scraping_method': scraped_data.get('scraping_method', 'unknown'),
                    'responsive_design_detected': scraped_data.get('responsive_breakpoints', {}).get('is_responsive', False),
                    'frameworks_detected': scraped_data.get('page_insights', {}).get('librariesDetected', ()),
                    'performance_score': self._calculate_performance_score(scraped_data)
                },
                'files': self._organize_generated_files(generated_code),
                'deployment_instructions': self._create_deployment_instructions(),
                'browserbase_insights': self._extract_browserbase_insights(scraped_data)
            }
            
            logger.info(f"Successfully completed AI cloning for {original_url}")
            return result
            
        except Exception as e:
            logger.error(f"Error in AI cloning process: {e}")
            raise Exception(f"AI cloning failed: {str(e)}")
    
    def _create_enhanced_analysis_prompt(self, scraped_data: Dict[str, Any], url: str) -> str:
        """Create enhanced analysis prompt with Browserbase data"""
        
        # Extract enhanced data from Browserbase scraping
        layout_data = scraped_data.get('layout', {})
        performance_data = scraped_data.get('performance', {})
        responsive_data = scraped_data.get('responsive_breakpoints', {})
        page_insights = scraped_data.get('page_insights', {})
        screenshots = scraped_data.get('screenshots', {})
        
        structure_summary = self._summarize_enhanced_structure(scraped_data)
        
        prompt = f"""
You are an expert web developer tasked with analyzing a website to create a faithful clone using advanced browser automation data.

WEBSITE TO ANALYZE: {url}

BASIC INFORMATION:
- Title: {scraped_data.get('title', 'N/A')}
- Description: {scraped_data.get('meta_description', 'N/A')}
- Language: {scraped_data.get('language', 'en')}
- Word Count: {scraped_data.get('word_count', 0)}

ENHANCED BROWSER DATA:
- Scraping Method: {scraped_data.get('scraping_method', 'unknown')}
- Browserbase Used: {scraped_data.get('browserbase_used', False)}
- Screenshots Available: {', '.join(screenshots.keys()) if screenshots else 'None'}

PERFORMANCE METRICS:
- Load Time: {performance_data.get('loadTime', 0)}ms
- First Paint: {performance_data.get('firstPaint', 0)}ms
- First Contentful Paint: {performance_data.get('firstContentfulPaint', 0)}ms
- Resource Count: {performance_data.get('resourceCount', 0)}
- Total Resource Size: {performance_data.get('totalResourceSize', 0)} bytes

RESPONSIVE DESIGN:
- Is Responsive: {responsive_data.get('is_responsive', False)}
- Has Media Queries: {responsive_data.get('has_media_queries', False)}
- Viewport Meta: {responsive_data.get('viewport_meta', 'None')}

PAGE INSIGHTS:
- Total Elements: {page_insights.get('elementCounts', {}).get('total', 0)}
- Images: {page_insights.get('elementCounts', {}).get('images', 0)}
- Links: {page_insights.get('elementCounts', {}).get('links', 0)}
- Forms: {page_insights.get('elementCounts', {}).get('forms', 0)}
- Frameworks Detected: {', '.join(page_insights.get('librariesDetected', []))}

LAYOUT STRUCTURE:
{structure_summary}

COMPUTED COLORS: {', '.join(page_insights.get('computedColors', [])[:15])}
EXTRACTED COLORS: {', '.join(scraped_data.get('colors', [])[:10])}
FONTS USED: {', '.join(scraped_data.get('fonts', [])[:5])}

NAVIGATION STRUCTURE:
{self._summarize_navigation(scraped_data)}

FORMS AND INTERACTIONS:
{self._summarize_forms(scraped_data)}

SOCIAL MEDIA INTEGRATION:
{self._summarize_social_media(scraped_data)}

ANALYTICS & TRACKING:
{self._summarize_analytics(scraped_data)}

Please analyze this website and provide:

1. **Enhanced Design Analysis**:
   - Design style and aesthetic based on computed styles
   - Layout patterns (flexbox, grid, traditional)
   - Visual hierarchy and typography approach
   - Color scheme analysis with specific values
   - Responsive design implementation strategy

2. **Technical Architecture Assessment**:
   - HTML structure recommendations based on semantic elements
   - CSS framework requirements (detected: {', '.join(page_insights.get('librariesDetected', []))})
   - JavaScript functionality requirements
   - Performance optimization needs
   - Mobile-first vs desktop-first approach

3. **Component Priority Analysis**:
   - Critical elements for visual fidelity
   - Interactive components that need recreation
   - Content organization and hierarchy
   - Navigation patterns to preserve

4. **Implementation Strategy**:
   - Recommended tech stack for optimal clone
   - Development approach based on responsive analysis
   - Performance considerations from metrics
   - Accessibility requirements

5. **Content and Media Strategy**:
   - Image optimization recommendations
   - Content structure preservation
   - Media query breakpoints
   - Font loading strategies

Provide your analysis in a structured JSON format with clear sections for each area.
"""
        return prompt
    
    def _create_enhanced_code_generation_prompt(self, scraped_data: Dict[str, Any], analysis: str) -> str:
        """Create enhanced code generation prompt with Browserbase insights"""
        
        layout_data = scraped_data.get('layout', {})
        responsive_data = scraped_data.get('responsive_breakpoints', {})
        page_insights = scraped_data.get('page_insights', {})
        
        prompt = f"""
Based on the following enhanced website analysis using cloud browser automation, generate a complete, modern website clone.

ENHANCED ANALYSIS RESULTS:
{analysis}

ORIGINAL WEBSITE DATA:
- Title: {scraped_data.get('title', 'Website Clone')}
- Key Content: {self._extract_sample_content(scraped_data)}
- Structure: {self._summarize_enhanced_structure(scraped_data)}
- Navigation: {self._summarize_navigation(scraped_data)}

BROWSER AUTOMATION INSIGHTS:
- Total Elements: {page_insights.get('elementCounts', {}).get('total', 0)}
- Frameworks Detected: {', '.join(page_insights.get('librariesDetected', []))}
- Responsive Design: {responsive_data.get('is_responsive', False)}
- Viewport Settings: {responsive_data.get('viewport_meta', 'width=device-width, initial-scale=1')}

LAYOUT CONTAINERS ({len(layout_data.get('containers', []))} analyzed):
{self._format_layout_containers(layout_data)}

RESPONSIVE BREAKPOINTS:
{self._format_responsive_breakpoints(responsive_data)}

PERFORMANCE REQUIREMENTS:
- Optimize for {page_insights.get('elementCounts', {}).get('images', 0)} images
- Consider {len(scraped_data.get('scripts', {}).get('external', []))} external scripts
- Target load time: < 3 seconds

REQUIREMENTS:
1. Create a modern, responsive website using HTML5, CSS3, and vanilla JavaScript
2. Use semantic HTML structure matching the analyzed layout
3. Implement mobile-first responsive design with detected breakpoints
4. Include proper meta tags and SEO optimization
5. Use modern CSS features (Flexbox, Grid, CSS Variables)
6. Add smooth animations and transitions
7. Ensure accessibility (ARIA labels, semantic markup)
8. Include placeholder content that matches the original's theme
9. Optimize for performance based on analysis

SPECIFIC DELIVERABLES:
1. **index.html** - Complete HTML structure with semantic elements
2. **styles.css** - Complete CSS with responsive design and performance optimization
3. **script.js** - JavaScript for interactions and framework compatibility
4. **README.md** - Setup and customization instructions

STYLING GUIDELINES:
- Primary Colors: {', '.join(page_insights.get('computedColors', ['#333333', '#ffffff'])[:5])}
- Extracted Colors: {', '.join(scraped_data.get('colors', ['#000000'])[:5])}
- Font Families: {', '.join(scraped_data.get('fonts', ['Arial, sans-serif'])[:3])}
- Layout Pattern: {'Grid-based' if 'grid' in str(layout_data) else 'Flexbox-based'}
- Responsive: {'Mobile-first' if responsive_data.get('is_responsive') else 'Desktop-only'}

CONTENT GUIDELINES:
- Use realistic placeholder content matching the {scraped_data.get('word_count', 0)} word count
- Maintain the same content structure and flow
- Include proper headings hierarchy ({len(scraped_data.get('structure', {}).get('headings', []))} headings detected)
- Add relevant placeholder images and media

FRAMEWORK COMPATIBILITY:
{self._get_framework_recommendations(page_insights.get('librariesDetected', []))}

Generate complete, production-ready code that creates a beautiful, functional website clone.
Provide each file's complete code, properly formatted and commented.
Focus on pixel-perfect recreation while maintaining modern web standards.
"""
        return prompt
    
    def _summarize_enhanced_structure(self, scraped_data: Dict[str, Any]) -> str:
        """Create enhanced structure summary with layout data"""
        structure = scraped_data.get('structure', {})
        layout = scraped_data.get('layout', {})
        
        headings = structure.get('headings', [])
        semantic_elements = structure.get('semantic_elements', [])
        containers = layout.get('containers', [])
        
        summary = f"HTML Structure Analysis:\n"
        summary += f"- Headings: {len(headings)} found (H1-H6 hierarchy)\n"
        summary += f"- Semantic elements: {len(semantic_elements)} found\n"
        summary += f"- Layout containers: {len(containers)} analyzed\n"
        
        if headings:
            summary += "Heading hierarchy: "
            for h in headings[:5]:  # First 5 headings
                summary += f"H{h.get('level')} '{h.get('text', '')[:30]}', "
            summary = summary.rstrip(', ') + "\n"
        
        if semantic_elements:
            summary += "Semantic tags: "
            tags = [el.get('tag') for el in semantic_elements]
            summary += ', '.join(set(tags)) + "\n"
        
        if containers:
            summary += "Layout containers: "
            container_types = [c.get('tagName', '').lower() for c in containers[:10]]
            summary += ', '.join(set(container_types))
        
        return summary
    
    def _format_layout_containers(self, layout_data: Dict[str, Any]) -> str:
        """Format layout container information"""
        containers = layout_data.get('containers', [])
        if not containers:
            return "No layout containers analyzed"
        
        summary = []
        for i, container in enumerate(containers[:10]):  # First 10 containers
            position = container.get('position', {})
            styles = container.get('styles', {})
            
            container_desc = f"{i+1}. <{container.get('tagName', 'div').lower()}"
            if container.get('className'):
                container_desc += f" class='{container.get('className')[:50]}'"
            if container.get('id'):
                container_desc += f" id='{container.get('id')}'"
            
            container_desc += f"> - {styles.get('display', 'block')} layout"
            container_desc += f" ({position.get('width', 0)}x{position.get('height', 0)}px)"
            
            if styles.get('backgroundColor') and styles.get('backgroundColor') != 'rgba(0, 0, 0, 0)':
                container_desc += f" bg: {styles.get('backgroundColor')}"
            
            summary.append(container_desc)
        
        return '\n'.join(summary)
    
    def _format_responsive_breakpoints(self, responsive_data: Dict[str, Any]) -> str:
        """Format responsive breakpoint information"""
        breakpoints = responsive_data.get('breakpoint_tests', [])
        if not breakpoints:
            return "No responsive breakpoints tested"
        
        summary = []
        for bp in breakpoints:
            bp_desc = f"- {bp.get('width')}px: "
            bp_desc += f"container max-width: {bp.get('containerMaxWidth', 'auto')}, "
            bp_desc += f"font-size: {bp.get('fontSize', 'inherit')}"
            summary.append(bp_desc)
        
        return '\n'.join(summary)
    
    def _get_framework_recommendations(self, detected_frameworks: List[str]) -> str:
        """Get framework-specific recommendations"""
        if not detected_frameworks:
            return "- Use vanilla HTML/CSS/JS for maximum compatibility"
        
        recommendations = []
        for framework in detected_frameworks:
            if framework.lower() == 'react':
                recommendations.append("- Consider React-like component structure")
            elif framework.lower() == 'vue':
                recommendations.append("- Implement Vue.js-style reactive components")
            elif framework.lower() == 'jquery':
                recommendations.append("- Include jQuery-compatible DOM manipulation")
            elif framework.lower() == 'bootstrap':
                recommendations.append("- Use Bootstrap-compatible grid system and utilities")
            elif 'tailwind' in framework.lower():
                recommendations.append("- Implement utility-first CSS approach")
        
        return '\n'.join(recommendations) if recommendations else "- Use vanilla JS for detected framework compatibility"
    
    def _extract_browserbase_insights(self, scraped_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract insights specific to Browserbase scraping"""
        return {
            'browserbase_used': scraped_data.get('browserbase_used', False),
            'scraping_method': scraped_data.get('scraping_method', 'unknown'),
            'screenshots_captured': list(scraped_data.get('screenshots', {}).keys()),
            'performance_metrics': scraped_data.get('performance', {}),
            'responsive_tested': scraped_data.get('responsive_breakpoints', {}).get('is_responsive', False),
            'frameworks_detected': scraped_data.get('page_insights', {}).get('librariesDetected', []),
            'total_elements': scraped_data.get('page_insights', {}).get('elementCounts', {}).get('total', 0),
            'computed_colors_count': len(scraped_data.get('page_insights', {}).get('computedColors', [])),
            'layout_containers_analyzed': len(scraped_data.get('layout', {}).get('containers', []))
        }
    
    
    
    def _calculate_performance_score(self, scraped_data: Dict[str, Any]) -> float:
        """Calculate performance score based on Browserbase metrics"""
        performance = scraped_data.get('performance', {})
        page_insights = scraped_data.get('page_insights', {})
        
        score = 100.0
        
        # Deduct for slow load times
        load_time = performance.get('loadTime', 0)
        if load_time > 3000:  # 3 seconds
            score -= min(30, (load_time - 3000) / 100)
        
        # Deduct for large resource count
        resource_count = performance.get('resourceCount', 0)
        if resource_count > 50:
            score -= min(20, (resource_count - 50) * 0.5)
        
        # Deduct for large resource size
        total_size = performance.get('totalResourceSize', 0)
        if total_size > 1000000:  # 1MB
            score -= min(25, (total_size - 1000000) / 100000)
        
        # Deduct for excessive DOM elements
        total_elements = page_insights.get('elementCounts', {}).get('total', 0)
        if total_elements > 1500:
            score -= min(15, (total_elements - 1500) / 100)
        
        return max(0, score)
    
    def _summarize_social_media(self, scraped_data: Dict[str, Any]) -> str:
        """Summarize social media integration"""
        social_media = scraped_data.get('social_media', {})
        og_tags = social_media.get('og_tags', {})
        twitter_cards = social_media.get('twitter_cards', {})
        social_links = social_media.get('social_links', [])
        
        if not any([og_tags, twitter_cards, social_links]):
            return "No social media integration detected"
        
        summary = []
        if og_tags:
            summary.append(f"Open Graph tags: {len(og_tags)} found")
        if twitter_cards:
            summary.append(f"Twitter Card tags: {len(twitter_cards)} found")
        if social_links:
            platforms = list(set(link.get('platform') for link in social_links))
            summary.append(f"Social links: {', '.join(platforms)}")
        
        return '; '.join(summary)
    
    def _summarize_analytics(self, scraped_data: Dict[str, Any]) -> str:
        """Summarize analytics and tracking"""
        analytics = scraped_data.get('analytics', {})
        
        tracking_found = []
        if analytics.get('google_analytics'):
            tracking_found.append(f"Google Analytics ({len(analytics['google_analytics'])} IDs)")
        if analytics.get('google_tag_manager'):
            tracking_found.append(f"Google Tag Manager ({len(analytics['google_tag_manager'])} IDs)")
        if analytics.get('facebook_pixel'):
            tracking_found.append(f"Facebook Pixel ({len(analytics['facebook_pixel'])} IDs)")
        if analytics.get('other_tracking'):
            tracking_found.append(f"Other tracking: {', '.join(analytics['other_tracking'])}")
        
        return '; '.join(tracking_found) if tracking_found else "No analytics tracking detected"
    
    # Keep all existing methods from your original LLMWebsiteCloner class
    def _extract_key_content(self, scraped_data: Dict[str, Any]) -> str:
        """Extract key content sections"""
        text_content = scraped_data.get('text_content', '')
        # Get first 500 characters as sample
        return text_content[:500] + "..." if len(text_content) > 500 else text_content
    
    def _extract_sample_content(self, scraped_data: Dict[str, Any]) -> str:
        """Extract sample content for code generation"""
        text_content = scraped_data.get('text_content', '')
        # Get first 200 characters as sample
        return text_content[:200] + "..." if len(text_content) > 200 else text_content
    
    def _summarize_navigation(self, scraped_data: Dict[str, Any]) -> str:
        """Summarize navigation structure"""
        nav_data = scraped_data.get('navigation', {})
        nav_elements = nav_data.get('nav_elements', [])
        
        if not nav_elements:
            return "No navigation elements found"
        
        summary = f"Navigation elements: {len(nav_elements)}\n"
        for nav in nav_elements[:3]:  # First 3 nav elements
            links = nav.get('links', [])
            summary += f"Nav with {len(links)} links: "
            link_texts = [link.get('text', '') for link in links[:5]]
            summary += ', '.join(link_texts) + "\n"
        
        return summary.strip()
    
    def _summarize_forms(self, scraped_data: Dict[str, Any]) -> str:
        """Summarize forms and interactions"""
        forms = scraped_data.get('forms', [])
        
        if not forms:
            return "No forms found"
        
        summary = f"Forms found: {len(forms)}\n"
        for form in forms[:3]:  # First 3 forms
            fields = form.get('fields', [])
            summary += f"Form with {len(fields)} fields, method: {form.get('method', 'GET')}\n"
        
        return summary.strip()
    
    def _count_elements(self, scraped_data: Dict[str, Any]) -> int:
        """Count total elements analyzed"""
        count = 0
        count += len(scraped_data.get('images', []))
        count += sum(len(links) for links in scraped_data.get('links', {}).values())
        count += len(scraped_data.get('forms', []))
        count += len(scraped_data.get('structure', {}).get('headings', []))
        
        # Add browser-specific counts
        page_insights = scraped_data.get('page_insights', {})
        if page_insights:
            count += page_insights.get('elementCounts', {}).get('total', 0)
        
        return count
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    async def _get_ai_analysis(self, prompt: str) -> str:
        """Get AI analysis of the website"""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                temperature=0.3,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Error getting AI analysis: {e}")
            raise Exception(f"AI analysis failed: {str(e)}")
    
    async def _generate_code(self, prompt: str) -> Dict[str, str]:
        """Generate the actual website code"""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=8000,
                temperature=0.2,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            # Parse the generated code into separate files
            generated_text = response.content[0].text
            return self._parse_generated_code(generated_text)
            
        except Exception as e:
            logger.error(f"Error generating code: {e}")
            raise Exception(f"Code generation failed: {str(e)}")
    
    def _parse_generated_code(self, generated_text: str) -> Dict[str, str]:
        """Parse the generated text into separate files"""
        files = {}
        
        # Common file patterns to look for
        file_patterns = {
            'index.html': [r'```html\n(.*?)```', r'index\.html.*?\n(.*?)(?=\n\n|\n```|\nstyles\.css|\nscript\.js|$)'],
            'styles.css': [r'```css\n(.*?)```', r'styles\.css.*?\n(.*?)(?=\n\n|\n```|\nindex\.html|\nscript\.js|$)'],
            'script.js': [r'```javascript\n(.*?)```', r'```js\n(.*?)```', r'script\.js.*?\n(.*?)(?=\n\n|\n```|\nindex\.html|\nstyles\.css|$)'],
            'README.md': [r'```markdown\n(.*?)```', r'README\.md.*?\n(.*?)(?=\n\n|\n```|$)']
        }
        
        import re
        
        for filename, patterns in file_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, generated_text, re.DOTALL | re.IGNORECASE)
                if match:
                    files[filename] = match.group(1).strip()
                    break
        
        # If no specific patterns found, create basic structure
        if not files:
            files = self._create_fallback_files(generated_text)
        
        return files
    
    def _create_fallback_files(self, generated_text: str) -> Dict[str, str]:
        """Create fallback files if parsing fails"""
        return {
            'index.html': '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Website Clone</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <header>
        <h1>Website Clone</h1>
        <nav>
            <ul>
                <li><a href="#home">Home</a></li>
                <li><a href="#about">About</a></li>
                <li><a href="#contact">Contact</a></li>
            </ul>
        </nav>
    </header>
    
    <main>
        <section id="home">
            <h2>Welcome</h2>
            <p>This is a cloned website created using AI and Browserbase.</p>
        </section>
    </main>
    
    <footer>
        <p>&copy; 2024 Website Clone - Powered by Browserbase</p>
    </footer>
    
    <script src="script.js"></script>
</body>
</html>''',
            'styles.css': '''/* Website Clone Styles - Generated with Browserbase */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    line-height: 1.6;
    color: #333;
    background-color: #fff;
}

header {
    background: #333;
    color: #fff;
    padding: 1rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

nav ul {
    list-style: none;
    display: flex;
    gap: 1rem;
}

nav a {
    color: #fff;
    text-decoration: none;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    transition: background-color 0.3s ease;
}

nav a:hover {
    background-color: rgba(255,255,255,0.1);
}

main {
    padding: 2rem;
    max-width: 1200px;
    margin: 0 auto;
}

footer {
    background: #333;
    color: #fff;
    text-align: center;
    padding: 1rem;
    margin-top: 2rem;
}

/* Responsive Design */
@media (max-width: 768px) {
    nav ul {
        flex-direction: column;
        gap: 0.5rem;
    }
    
    main {
        padding: 1rem;
    }
}''',
            'script.js': '''// Website Clone JavaScript - Enhanced with Browserbase insights
document.addEventListener('DOMContentLoaded', function() {
    console.log('Website clone loaded successfully');
    console.log('Generated with Browserbase cloud browser automation');
    
    // Add smooth scrolling for navigation links
    const navLinks = document.querySelectorAll('nav a[href^="#"]');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ 
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Add loading animation
    const body = document.body;
    body.style.opacity = '0';
    body.style.transition = 'opacity 0.3s ease-in-out';
    
    window.addEventListener('load', function() {
        body.style.opacity = '1';
    });
    
    // Performance monitoring (inspired by Browserbase metrics)
    if ('performance' in window) {
        window.addEventListener('load', function() {
            setTimeout(function() {
                const perfData = performance.getEntriesByType('navigation')[0];
                if (perfData) {
                    console.log('Page Load Time:', perfData.loadEventEnd - perfData.loadEventStart, 'ms');
                }
            }, 0);
        });
    }
});''',
            'README.md': '''# Website Clone - Powered by Browserbase

This is an AI-generated clone of a website created using advanced browser automation technology.

## Features

- ✨ Generated using Browserbase cloud browsers
- 🎨 Pixel-perfect design recreation
- 📱 Responsive design with mobile optimization
- ⚡ Performance optimized
- 🧠 AI-powered code generation with Claude

## Setup Instructions

1. Download all files to a folder
2. Open `index.html` in a web browser
3. Customize the content as needed

## Files Included

- `index.html` - Main HTML structure with semantic markup
- `styles.css` - CSS styling with responsive design
- `script.js` - JavaScript functionality and interactions
- `README.md` - This documentation file

## Technology Stack

- **HTML5** - Semantic markup and structure
- **CSS3** - Modern styling with Flexbox/Grid
- **Vanilla JavaScript** - Enhanced interactions
- **Browserbase** - Cloud browser automation for data extraction
- **Claude AI** - Intelligent code generation

## Customization

You can modify the content, colors, and layout by editing the respective files.
The design is based on analysis from real browser automation data.

## Performance

This clone is optimized based on performance metrics gathered during the analysis phase.

## Browser Compatibility

- ✅ Chrome/Chromium (tested with Browserbase)
- ✅ Firefox
- ✅ Safari
- ✅ Edge

---

Generated with ❤️ using Browserbase and Claude AI
'''
        }
    
    def _organize_generated_files(self, generated_code: Dict[str, str]) -> Dict[str, Any]:
        """Organize generated files with metadata"""
        files = {}
        
        for filename, content in generated_code.items():
            files[filename] = {
                'content': content,
                'size': len(content),
                'type': self._get_file_type(filename),
                'description': self._get_file_description(filename),
                'lines': len(content.splitlines()),
                'enhanced_with_browserbase': True
            }
        
        return files
    
    def _get_file_type(self, filename: str) -> str:
        """Get file type based on extension"""
        extension = filename.split('.')[-1].lower()
        type_mapping = {
            'html': 'text/html',
            'css': 'text/css',
            'js': 'application/javascript',
            'md': 'text/markdown'
        }
        return type_mapping.get(extension, 'text/plain')
    
    def _get_file_description(self, filename: str) -> str:
        """Get enhanced file description"""
        descriptions = {
            'index.html': 'Main HTML structure with semantic markup and Browserbase insights',
            'styles.css': 'CSS styling with responsive design based on browser automation analysis',
            'script.js': 'JavaScript functionality enhanced with performance monitoring',
            'README.md': 'Setup instructions and documentation with Browserbase attribution'
        }
        return descriptions.get(filename, 'Generated file with Browserbase enhancement')
    
    def _create_deployment_instructions(self) -> Dict[str, str]:
        """Create enhanced deployment instructions"""
        return {
            'local_development': 'Open index.html in a web browser or use a local server for full functionality',
            'static_hosting': 'Upload all files to any static hosting service (Netlify, Vercel, GitHub Pages)',
            'customization': 'Edit the files to customize content, styling, and functionality. Design based on Browserbase analysis.',
            'requirements': 'No build process required - pure HTML/CSS/JS enhanced with browser automation insights',
            'performance': 'Optimized based on real browser performance metrics from Browserbase',
            'responsive': 'Mobile-first responsive design tested across multiple viewport sizes'
        }
    
    # Add this simple method to your LLMWebsiteCloner class

    async def generate_enhanced_clone(self, scraped_data: Dict[str, Any], preferences: Optional[Dict[str, Any]] = None, progress_callback: Optional[callable] = None) -> Dict[str, Any]:
        """
        Wrapper method for backward compatibility
        """
        try:
        # Use existing generate_clone method if it exists
            if hasattr(self, 'generate_clone'):
                result = await self.generate_clone(scraped_data)
            else:
            # Fallback to basic generation
                result = await self._generate_basic_clone(scraped_data)
        
        # Ensure result has the expected structure
            if not isinstance(result, dict) or 'files' not in result:
                raise Exception("Invalid clone result structure")
        
        # Add missing metadata fields
            if 'clone_metadata' not in result:
                result['clone_metadata'] = {
                    'title': scraped_data.get('title', 'Cloned Website'),
                    'description': scraped_data.get('description', 'AI-generated clone'),
                    'generation_timestamp': scraped_data.get('timestamp', ''),
                    'ai_model_used': 'Claude',
                    'browserbase_used': scraped_data.get('browserbase_used', False),
                    'scraping_method': scraped_data.get('scraping_method', 'local_playwright')
                }
        
            return result
        
        except Exception as e:
            raise Exception(f"Enhanced clone generation failed: {str(e)}")

    async def _generate_basic_clone(self, scraped_data: Dict[str, Any]) -> Dict[str, Any]:
        """Basic clone generation fallback"""
    
        title = scraped_data.get('title', 'Cloned Website')
        content = scraped_data.get('content', '')
    
    # Basic HTML
        html_content = f'''<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <link rel="stylesheet" href="styles.css">
    </head>
    <body>
        <h1>{title}</h1>
        <div class="content">
            <p>This website has been cloned using AI.</p>
        </div>
        <script src="script.js"></script>
    </body>
    </html>'''
    
    # Basic CSS
        css_content = '''
    body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
    h1 { color: #333; }
    .content { margin-top: 20px; }
    '''
    
    # Basic JS
        js_content = '''
    console.log('Website clone loaded');
    '''
    
        return {
            'files': {
                'index.html': {
                    'content': html_content,
                    'size': len(html_content.encode('utf-8')),
                    'type': 'text/html',
                    'description': 'Main HTML file'
                },
                'styles.css': {
                    'content': css_content,
                    'size': len(css_content.encode('utf-8')),
                    'type': 'text/css',
                    'description': 'CSS styles'
                },
                'script.js': {
                    'content': js_content,
                    'size': len(js_content.encode('utf-8')),
                'type': 'application/javascript',
                'description': 'JavaScript functionality'
            }
        }
    }
    


# # llm_cloner.py - AI-Powered Website Cloning

# import os
# from typing import Dict, Any, List
# import json
# from dotenv import load_dotenv
# import logging
# from anthropic import Anthropic
# from .utils import measure_performance, retry_async, setup_logging
# load_dotenv()
# logger = logging.getLogger(__name__)

# class LLMWebsiteCloner:
    
#     def __init__(self):
#         # Initialize Anthropic client
#         api_key = os.getenv('ANTHROPIC_API_KEY')
#         if not api_key:
#             raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        
#         self.client = Anthropic(api_key=api_key)
#         self.model = "claude-3-5-sonnet-20241022"
    
#     @retry_async(max_retries=2)
#     @measure_performance
#     async def clone_website(self, scraped_data: Dict[str, Any], original_url: str) -> Dict[str, Any]:
#         """
#         Use AI to generate a clone of the website based on scraped data
#         """
#         logger.info(f"Starting AI cloning process for {original_url}")
        
#         try:
#             # Prepare the context for the AI
#             analysis_prompt = self._create_analysis_prompt(scraped_data, original_url)
            
#             # Get AI analysis and recommendations
#             analysis = await self._get_ai_analysis(analysis_prompt)
            
#             # Generate HTML/CSS/JS code
#             code_generation_prompt = self._create_code_generation_prompt(scraped_data, analysis)
#             generated_code = await self._generate_code(code_generation_prompt)
            
#             # Create the final result
#             result = {
#                 'original_url': original_url,
#                 'analysis': analysis,
#                 'generated_code': generated_code,
#                 'clone_metadata': {
#                     'title': scraped_data.get('title', 'Cloned Website'),
#                     'description': scraped_data.get('meta_description', ''),
#                     'generation_timestamp': self._get_timestamp(),
#                     'total_elements_analyzed': self._count_elements(scraped_data),
#                     'ai_model_used': self.model
#                 },
#                 'files': self._organize_generated_files(generated_code),
#                 'deployment_instructions': self._create_deployment_instructions()
#             }
            
#             logger.info(f"Successfully completed AI cloning for {original_url}")
#             return result
            
#         except Exception as e:
#             logger.error(f"Error in AI cloning process: {e}")
#             raise Exception(f"AI cloning failed: {str(e)}")
    
#     def _create_analysis_prompt(self, scraped_data: Dict[str, Any], url: str) -> str:
#         """Create the prompt for AI analysis of the website"""
        
#         structure_summary = self._summarize_structure(scraped_data)
        
#         prompt = f"""
# You are an expert web developer tasked with analyzing a website to create a faithful clone. 

# WEBSITE TO ANALYZE: {url}

# WEBSITE DATA:
# Title: {scraped_data.get('title', 'N/A')}
# Description: {scraped_data.get('meta_description', 'N/A')}

# STRUCTURE SUMMARY:
# {structure_summary}

# COLOR PALETTE: {', '.join(scraped_data.get('colors', [])[:10])}
# FONTS USED: {', '.join(scraped_data.get('fonts', [])[:5])}

# KEY CONTENT SECTIONS:
# {self._extract_key_content(scraped_data)}

# NAVIGATION STRUCTURE:
# {self._summarize_navigation(scraped_data)}

# FORMS AND INTERACTIONS:
# {self._summarize_forms(scraped_data)}

# Please analyze this website and provide:

# 1. **Overall Design Analysis**:
#    - Design style and aesthetic (modern, classic, minimalist, etc.)
#    - Layout patterns used (grid, flexbox, etc.)
#    - Visual hierarchy and typography approach
#    - Color scheme and branding elements

# 2. **Technical Architecture**:
#    - HTML structure recommendations
#    - CSS framework needs (if any)
#    - JavaScript requirements
#    - Responsive design approach

# 3. **Key Components to Recreate**:
#    - Priority order of elements to implement
#    - Critical functionality to preserve
#    - Interactive elements that need attention
#    - Content organization strategy

# 4. **Implementation Strategy**:
#    - Recommended tech stack for clone
#    - Development approach (mobile-first, etc.)
#    - Performance considerations
#    - Accessibility requirements

# 5. **Content Strategy**:
#    - How to handle dynamic content
#    - Placeholder text recommendations
#    - Image and media handling

# Provide your analysis in a structured JSON format with clear sections for each area.
# """
#         return prompt
    
#     def _create_code_generation_prompt(self, scraped_data: Dict[str, Any], analysis: str) -> str:
#         """Create the prompt for generating the actual code"""
        
#         prompt = f"""
# Based on the following website analysis, generate a complete, modern website clone.

# ANALYSIS RESULTS:
# {analysis}

# ORIGINAL WEBSITE DATA:
# - Title: {scraped_data.get('title', 'Website Clone')}
# - Key Content: {self._extract_sample_content(scraped_data)}
# - Structure: {self._summarize_structure(scraped_data)}
# - Navigation: {self._summarize_navigation(scraped_data)}

# REQUIREMENTS:
# 1. Create a modern, responsive website using HTML5, CSS3, and vanilla JavaScript
# 2. Use semantic HTML structure
# 3. Implement mobile-first responsive design
# 4. Include proper meta tags and SEO optimization
# 5. Use modern CSS features (Flexbox, Grid, CSS Variables)
# 6. Add smooth animations and transitions
# 7. Ensure accessibility (ARIA labels, semantic markup)
# 8. Include placeholder content that matches the original's theme

# SPECIFIC DELIVERABLES:
# 1. **index.html** - Complete HTML structure
# 2. **styles.css** - Complete CSS with responsive design
# 3. **script.js** - JavaScript for interactions
# 4. **README.md** - Setup and customization instructions

# STYLING GUIDELINES:
# - Use the color palette: {', '.join(scraped_data.get('colors', ['#333333', '#ffffff'])[:5])}
# - Font families: {', '.join(scraped_data.get('fonts', ['Arial, sans-serif'])[:3])}
# - Maintain the original's visual hierarchy and spacing
# - Ensure excellent mobile responsiveness

# CONTENT GUIDELINES:
# - Use realistic placeholder content that matches the original's purpose
# - Maintain the same content structure and flow
# - Include proper headings hierarchy (h1, h2, etc.)
# - Add relevant placeholder images and media

# Generate complete, production-ready code that creates a beautiful, functional website clone.
# Provide each file's complete code, properly formatted and commented.
# """
#         return prompt
    
#     async def _get_ai_analysis(self, prompt: str) -> str:
#         """Get AI analysis of the website"""
#         try:
#             response = self.client.messages.create(
#                 model=self.model,
#                 max_tokens=4000,
#                 temperature=0.3,
#                 messages=[{
#                     "role": "user",
#                     "content": prompt
#                 }]
#             )
            
#             return response.content[0].text
            
#         except Exception as e:
#             logger.error(f"Error getting AI analysis: {e}")
#             raise Exception(f"AI analysis failed: {str(e)}")
    
#     async def _generate_code(self, prompt: str) -> Dict[str, str]:
#         """Generate the actual website code"""
#         try:
#             response = self.client.messages.create(
#                 model=self.model,
#                 max_tokens=8000,
#                 temperature=0.2,
#                 messages=[{
#                     "role": "user",
#                     "content": prompt
#                 }]
#             )
            
#             # Parse the generated code into separate files
#             generated_text = response.content[0].text
#             return self._parse_generated_code(generated_text)
            
#         except Exception as e:
#             logger.error(f"Error generating code: {e}")
#             raise Exception(f"Code generation failed: {str(e)}")
    
#     def _parse_generated_code(self, generated_text: str) -> Dict[str, str]:
#         """Parse the generated text into separate files"""
#         files = {}
        
#         # Common file patterns to look for
#         file_patterns = {
#             'index.html': [r'```html\n(.*?)```', r'index\.html.*?\n(.*?)(?=\n\n|\n```|\nstyles\.css|\nscript\.js|$)'],
#             'styles.css': [r'```css\n(.*?)```', r'styles\.css.*?\n(.*?)(?=\n\n|\n```|\nindex\.html|\nscript\.js|$)'],
#             'script.js': [r'```javascript\n(.*?)```', r'```js\n(.*?)```', r'script\.js.*?\n(.*?)(?=\n\n|\n```|\nindex\.html|\nstyles\.css|$)'],
#             'README.md': [r'```markdown\n(.*?)```', r'README\.md.*?\n(.*?)(?=\n\n|\n```|$)']
#         }
        
#         import re
        
#         for filename, patterns in file_patterns.items():
#             for pattern in patterns:
#                 match = re.search(pattern, generated_text, re.DOTALL | re.IGNORECASE)
#                 if match:
#                     files[filename] = match.group(1).strip()
#                     break
        
#         # If no specific patterns found, create basic structure
#         if not files:
#             files = self._create_fallback_files(generated_text)
        
#         return files
    
#     def _create_fallback_files(self, generated_text: str) -> Dict[str, str]:
#         """Create fallback files if parsing fails"""
#         return {
#             'index.html': '''<!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <title>Website Clone</title>
#     <link rel="stylesheet" href="styles.css">
# </head>
# <body>
#     <header>
#         <h1>Website Clone</h1>
#         <nav>
#             <ul>
#                 <li><a href="#home">Home</a></li>
#                 <li><a href="#about">About</a></li>
#                 <li><a href="#contact">Contact</a></li>
#             </ul>
#         </nav>
#     </header>
    
#     <main>
#         <section id="home">
#             <h2>Welcome</h2>
#             <p>This is a cloned website created using AI.</p>
#         </section>
#     </main>
    
#     <footer>
#         <p>&copy; 2024 Website Clone</p>
#     </footer>
    
#     <script src="script.js"></script>
# </body>
# </html>''',
#             'styles.css': '''* {
#     margin: 0;
#     padding: 0;
#     box-sizing: border-box;
# }

# body {
#     font-family: Arial, sans-serif;
#     line-height: 1.6;
#     color: #333;
# }

# header {
#     background: #333;
#     color: #fff;
#     padding: 1rem;
# }

# nav ul {
#     list-style: none;
#     display: flex;
#     gap: 1rem;
# }

# nav a {
#     color: #fff;
#     text-decoration: none;
# }

# main {
#     padding: 2rem;
# }

# footer {
#     background: #333;
#     color: #fff;
#     text-align: center;
#     padding: 1rem;
# }''',
#             'script.js': '''// Website Clone JavaScript
# document.addEventListener('DOMContentLoaded', function() {
#     console.log('Website clone loaded successfully');
    
#     // Add smooth scrolling for navigation links
#     const navLinks = document.querySelectorAll('nav a[href^="#"]');
#     navLinks.forEach(link => {
#         link.addEventListener('click', function(e) {
#             e.preventDefault();
#             const target = document.querySelector(this.getAttribute('href'));
#             if (target) {
#                 target.scrollIntoView({ behavior: 'smooth' });
#             }
#         });
#     });
# });''',
#             'README.md': '''# Website Clone

# This is an AI-generated clone of a website.

# ## Setup Instructions

# 1. Download all files to a folder
# 2. Open `index.html` in a web browser
# 3. Customize the content as needed

# ## Files Included

# - `index.html` - Main HTML structure
# - `styles.css` - CSS styling
# - `script.js` - JavaScript functionality
# - `README.md` - This file

# ## Customization

# You can modify the content, colors, and layout by editing the respective files.
# '''
#         }
    
#     def _summarize_structure(self, scraped_data: Dict[str, Any]) -> str:
#         """Summarize the website structure"""
#         structure = scraped_data.get('structure', {})
#         headings = structure.get('headings', [])
#         semantic_elements = structure.get('semantic_elements', [])
        
#         summary = f"Headings: {len(headings)} found\n"
#         summary += f"Semantic elements: {len(semantic_elements)} found\n"
        
#         if headings:
#             summary += "Heading hierarchy: "
#             for h in headings[:5]:  # First 5 headings
#                 summary += f"H{h.get('level')} '{h.get('text', '')[:30]}', "
#             summary = summary.rstrip(', ') + "\n"
        
#         if semantic_elements:
#             summary += "Semantic tags: "
#             tags = [el.get('tag') for el in semantic_elements]
#             summary += ', '.join(set(tags))
        
#         return summary
    
#     def _extract_key_content(self, scraped_data: Dict[str, Any]) -> str:
#         """Extract key content sections"""
#         text_content = scraped_data.get('text_content', '')
#         # Get first 500 characters as sample
#         return text_content[:500] + "..." if len(text_content) > 500 else text_content
    
#     def _extract_sample_content(self, scraped_data: Dict[str, Any]) -> str:
#         """Extract sample content for code generation"""
#         text_content = scraped_data.get('text_content', '')
#         # Get first 200 characters as sample
#         return text_content[:200] + "..." if len(text_content) > 200 else text_content
    
#     def _summarize_navigation(self, scraped_data: Dict[str, Any]) -> str:
#         """Summarize navigation structure"""
#         nav_data = scraped_data.get('navigation', {})
#         nav_elements = nav_data.get('nav_elements', [])
        
#         if not nav_elements:
#             return "No navigation elements found"
        
#         summary = f"Navigation elements: {len(nav_elements)}\n"
#         for nav in nav_elements[:3]:  # First 3 nav elements
#             links = nav.get('links', [])
#             summary += f"Nav with {len(links)} links: "
#             link_texts = [link.get('text', '') for link in links[:5]]
#             summary += ', '.join(link_texts) + "\n"
        
#         return summary.strip()
    
#     def _summarize_forms(self, scraped_data: Dict[str, Any]) -> str:
#         """Summarize forms and interactions"""
#         forms = scraped_data.get('forms', [])
        
#         if not forms:
#             return "No forms found"
        
#         summary = f"Forms found: {len(forms)}\n"
#         for form in forms[:3]:  # First 3 forms
#             fields = form.get('fields', [])
#             summary += f"Form with {len(fields)} fields, method: {form.get('method', 'GET')}\n"
        
#         return summary.strip()
    
#     def _count_elements(self, scraped_data: Dict[str, Any]) -> int:
#         """Count total elements analyzed"""
#         count = 0
#         count += len(scraped_data.get('images', []))
#         count += len(scraped_data.get('links', []))
#         count += len(scraped_data.get('forms', []))
#         count += len(scraped_data.get('structure', {}).get('headings', []))
#         return count
    
#     def _get_timestamp(self) -> str:
#         """Get current timestamp"""
#         from datetime import datetime
#         return datetime.now().isoformat()
    
#     def _organize_generated_files(self, generated_code: Dict[str, str]) -> Dict[str, Any]:
#         """Organize generated files with metadata"""
#         files = {}
        
#         for filename, content in generated_code.items():
#             files[filename] = {
#                 'content': content,
#                 'size': len(content),
#                 'type': self._get_file_type(filename),
#                 'description': self._get_file_description(filename)
#             }
        
#         return files
    
#     def _get_file_type(self, filename: str) -> str:
#         """Get file type based on extension"""
#         extension = filename.split('.')[-1].lower()
#         type_mapping = {
#             'html': 'text/html',
#             'css': 'text/css',
#             'js': 'application/javascript',
#             'md': 'text/markdown'
#         }
#         return type_mapping.get(extension, 'text/plain')
    
#     def _get_file_description(self, filename: str) -> str:
#         """Get file description"""
#         descriptions = {
#             'index.html': 'Main HTML structure and content',
#             'styles.css': 'CSS styling and responsive design',
#             'script.js': 'JavaScript functionality and interactions',
#             'README.md': 'Setup instructions and documentation'
#         }
#         return descriptions.get(filename, 'Generated file')
    
#     def _create_deployment_instructions(self) -> Dict[str, str]:
#         """Create deployment instructions"""
#         return {
#             'local_development': 'Open index.html in a web browser or use a local server',
#             'static_hosting': 'Upload all files to any static hosting service (Netlify, Vercel, GitHub Pages)',
#             'customization': 'Edit the files to customize content, styling, and functionality',
#             'requirements': 'No build process required - pure HTML/CSS/JS'
#         }

#     async def generate_enhanced_clone(self, scraped_data: Dict[str, Any], original_url: str, 
#                                     user_preferences: Dict[str, Any] = None) -> Dict[str, Any]:
#         """
#         Generate an enhanced clone with user preferences
#         """
#         preferences = user_preferences or {}
        
#         # Create enhanced prompt with preferences
#         enhanced_prompt = self._create_enhanced_prompt(scraped_data, original_url, preferences)
        
#         # Generate enhanced code
#         enhanced_code = await self._generate_code(enhanced_prompt)
        
#         return {
#             'original_url': original_url,
#             'enhanced_code': enhanced_code,
#             'preferences_applied': preferences,
#             'files': self._organize_generated_files(enhanced_code)
#         }
    
#     def _create_enhanced_prompt(self, scraped_data: Dict[str, Any], url: str, 
#                               preferences: Dict[str, Any]) -> str:
#         """Create enhanced prompt with user preferences"""
        
#         base_prompt = self._create_code_generation_prompt(scraped_data, "")
        
#         # Add preference modifications
#         preference_text = ""
#         if preferences.get('color_scheme'):
#             preference_text += f"- Use color scheme: {preferences['color_scheme']}\n"
#         if preferences.get('layout_style'):
#             preference_text += f"- Apply layout style: {preferences['layout_style']}\n"
#         if preferences.get('fonts'):
#             preference_text += f"- Use fonts: {', '.join(preferences['fonts'])}\n"
#         if preferences.get('additional_features'):
#             preference_text += f"- Add features: {', '.join(preferences['additional_features'])}\n"
        
#         if preference_text:
#             enhanced_prompt = base_prompt + f"\n\nADDITIONAL USER PREFERENCES:\n{preference_text}"
#         else:
#             enhanced_prompt = base_prompt
        
#         return enhanced_prompt

#     def create_style_variations(self, base_code: Dict[str, str]) -> Dict[str, Dict[str, str]]:
#         """
#         Create different style variations of the generated code
#         """
#         variations = {
#             'modern': self._apply_modern_styling(base_code),
#             'minimal': self._apply_minimal_styling(base_code),
#             'classic': self._apply_classic_styling(base_code),
#             'dark': self._apply_dark_theme(base_code)
#         }
        
#         return variations
    
#     def _apply_modern_styling(self, base_code: Dict[str, str]) -> Dict[str, str]:
#         """Apply modern styling variations"""
#         # This would modify the CSS to use modern design patterns
#         modified_code = base_code.copy()
#         # Add modern CSS modifications here
#         return modified_code
    
#     def _apply_minimal_styling(self, base_code: Dict[str, str]) -> Dict[str, str]:
#         """Apply minimal styling variations"""
#         modified_code = base_code.copy()
#         # Add minimal design modifications here
#         return modified_code
    
#     def _apply_classic_styling(self, base_code: Dict[str, str]) -> Dict[str, str]:
#         """Apply classic styling variations"""
#         modified_code = base_code.copy()
#         # Add classic design modifications here
#         return modified_code
    
#     def _apply_dark_theme(self, base_code: Dict[str, str]) -> Dict[str, str]:
#         """Apply dark theme variations"""
#         modified_code = base_code.copy()
#         # Add dark theme modifications here
#         return modified_code