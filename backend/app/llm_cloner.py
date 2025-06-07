# llm_cloner.py - AI-Powered Website Cloning

import os
from typing import Dict, Any, List
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
        self._current_scraped_data = {}  # Initialize for fallback use
    
    @retry_async(max_retries=2)
    @measure_performance
    async def clone_website(self, scraped_data: Dict[str, Any], original_url: str) -> Dict[str, Any]:
        """
        Use AI to generate a clone of the website based on scraped data
        """
        logger.info(f"Starting AI cloning process for {original_url}")
        
        try:
            # Store scraped data for fallback use
            self._current_scraped_data = scraped_data
            
            # Prepare the context for the AI
            analysis_prompt = self._create_analysis_prompt(scraped_data, original_url)
            
            # Get AI analysis and recommendations
            analysis = await self._get_ai_analysis(analysis_prompt)
            
            # Generate HTML/CSS/JS code
            code_generation_prompt = self._create_code_generation_prompt(scraped_data, analysis)
            generated_code = await self._generate_code(code_generation_prompt)
            
            # Create the final result
            result = {
                'original_url': original_url,
                'analysis': analysis,
                'generated_code': generated_code,
                'clone_metadata': {
                    'title': scraped_data.get('title', 'Cloned Website'),
                    'description': scraped_data.get('meta_description', ''),
                    'generation_timestamp': self._get_timestamp(),
                    'total_elements_analyzed': self._count_elements(scraped_data),
                    'ai_model_used': self.model
                },
                'files': self._organize_generated_files(generated_code),
                'deployment_instructions': self._create_deployment_instructions()
            }
            
            logger.info(f"Successfully completed AI cloning for {original_url}")
            return result
            
        except Exception as e:
            logger.error(f"Error in AI cloning process: {e}")
            raise Exception(f"AI cloning failed: {str(e)}")

    async def generate_enhanced_clone(self, scraped_data: Dict[str, Any], original_url: str, 
                                    user_preferences: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate an enhanced clone with user preferences
        """
        logger.info(f"Starting enhanced AI cloning process for {original_url}")
        
        try:
            preferences = user_preferences or {}
            
            # Store scraped data for fallback use
            self._current_scraped_data = scraped_data
            
            # Get AI analysis first
            analysis_prompt = self._create_analysis_prompt(scraped_data, original_url)
            analysis = await self._get_ai_analysis(analysis_prompt)
            
            # Create enhanced prompt with preferences
            enhanced_prompt = self._create_enhanced_prompt(scraped_data, original_url, preferences)
            
            # Generate enhanced code
            enhanced_code = await self._generate_code(enhanced_prompt)
            
            # Create the final result with the same structure as clone_website
            result = {
                'original_url': original_url,
                'analysis': analysis,
                'generated_code': enhanced_code,
                'preferences_applied': preferences,
                'clone_metadata': {
                    'title': scraped_data.get('title', 'Enhanced Cloned Website'),
                    'description': scraped_data.get('meta_description', ''),
                    'generation_timestamp': self._get_timestamp(),
                    'total_elements_analyzed': self._count_elements(scraped_data),
                    'ai_model_used': self.model,
                    'preferences_used': bool(preferences)
                },
                'files': self._organize_generated_files(enhanced_code),
                'deployment_instructions': self._create_deployment_instructions()
            }
            
            logger.info(f"Successfully completed enhanced AI cloning for {original_url}")
            return result
            
        except Exception as e:
            logger.error(f"Error in enhanced AI cloning process: {e}")
            raise Exception(f"Enhanced AI cloning failed: {str(e)}")
    
    def _create_analysis_prompt(self, scraped_data: Dict[str, Any], url: str) -> str:
        """Create the prompt for AI analysis of the website"""
        
        structure_summary = self._summarize_structure(scraped_data)
        
        prompt = f"""
You are an expert web developer tasked with analyzing a website to create a faithful clone. 

WEBSITE TO ANALYZE: {url}

WEBSITE DATA:
Title: {scraped_data.get('title', 'N/A')}
Description: {scraped_data.get('meta_description', 'N/A')}

STRUCTURE SUMMARY:
{structure_summary}

COLOR PALETTE: {', '.join(scraped_data.get('colors', [])[:10])}
FONTS USED: {', '.join(scraped_data.get('fonts', [])[:5])}

KEY CONTENT SECTIONS:
{self._extract_key_content(scraped_data)}

NAVIGATION STRUCTURE:
{self._summarize_navigation(scraped_data)}

FORMS AND INTERACTIONS:
{self._summarize_forms(scraped_data)}

Please analyze this website and provide:

1. **Overall Design Analysis**:
   - Design style and aesthetic (modern, classic, minimalist, etc.)
   - Layout patterns used (grid, flexbox, etc.)
   - Visual hierarchy and typography approach
   - Color scheme and branding elements

2. **Technical Architecture**:
   - HTML structure recommendations
   - CSS framework needs (if any)
   - JavaScript requirements
   - Responsive design approach

3. **Key Components to Recreate**:
   - Priority order of elements to implement
   - Critical functionality to preserve
   - Interactive elements that need attention
   - Content organization strategy

4. **Implementation Strategy**:
   - Recommended tech stack for clone
   - Development approach (mobile-first, etc.)
   - Performance considerations
   - Accessibility requirements

5. **Content Strategy**:
   - How to handle dynamic content
   - Placeholder text recommendations
   - Image and media handling

Provide your analysis in a structured JSON format with clear sections for each area.
"""
        return prompt
    
    def _create_code_generation_prompt(self, scraped_data: Dict[str, Any], analysis: str) -> str:
        """Create the prompt for generating the actual code"""
        
        prompt = f"""
Based on the following website analysis, generate a complete, modern website clone.

ANALYSIS RESULTS:
{analysis}

ORIGINAL WEBSITE DATA:
- Title: {scraped_data.get('title', 'Website Clone')}
- Key Content: {self._extract_sample_content(scraped_data)}
- Structure: {self._summarize_structure(scraped_data)}
- Navigation: {self._summarize_navigation(scraped_data)}

REQUIREMENTS:
1. Create a modern, responsive website using HTML5, CSS3, and vanilla JavaScript
2. Use semantic HTML structure
3. Implement mobile-first responsive design
4. Include proper meta tags and SEO optimization
5. Use modern CSS features (Flexbox, Grid, CSS Variables)
6. Add smooth animations and transitions
7. Ensure accessibility (ARIA labels, semantic markup)
8. Include placeholder content that matches the original's theme

SPECIFIC DELIVERABLES:
1. **index.html** - Complete HTML structure
2. **styles.css** - Complete CSS with responsive design
3. **script.js** - JavaScript for interactions
4. **README.md** - Setup and customization instructions

STYLING GUIDELINES:
- Use the color palette: {', '.join(scraped_data.get('colors', ['#333333', '#ffffff'])[:5])}
- Font families: {', '.join(scraped_data.get('fonts', ['Arial, sans-serif'])[:3])}
- Maintain the original's visual hierarchy and spacing
- Ensure excellent mobile responsiveness

CONTENT GUIDELINES:
- Use realistic placeholder content that matches the original's purpose
- Maintain the same content structure and flow
- Include proper headings hierarchy (h1, h2, etc.)
- Add relevant placeholder images and media

Generate complete, production-ready code that creates a beautiful, functional website clone.
Provide each file's complete code, properly formatted and commented.
"""
        return prompt

    def _create_enhanced_prompt(self, scraped_data: Dict[str, Any], url: str, 
                              preferences: Dict[str, Any]) -> str:
        """Create enhanced prompt with user preferences"""
        
        base_prompt = self._create_code_generation_prompt(scraped_data, "")
        
        # Add preference modifications
        preference_text = ""
        if preferences.get('color_scheme'):
            preference_text += f"- Use color scheme: {preferences['color_scheme']}\n"
        if preferences.get('layout_style'):
            preference_text += f"- Apply layout style: {preferences['layout_style']}\n"
        if preferences.get('fonts'):
            preference_text += f"- Use fonts: {', '.join(preferences['fonts'])}\n"
        if preferences.get('additional_features'):
            preference_text += f"- Add features: {', '.join(preferences['additional_features'])}\n"
        if preferences.get('style'):
            preference_text += f"- Apply style theme: {preferences['style']}\n"
        if preferences.get('responsive'):
            preference_text += f"- Responsive design: {preferences['responsive']}\n"
        
        if preference_text:
            enhanced_prompt = base_prompt + f"\n\nADDITIONAL USER PREFERENCES:\n{preference_text}\n\nPlease incorporate these preferences while maintaining the core structure and content from the scraped data."
        else:
            enhanced_prompt = base_prompt
        
        return enhanced_prompt
    
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
        
        # If no specific patterns found, create enhanced structure using scraped data
        if not files:
            files = self._create_fallback_files(self._current_scraped_data, generated_text)
        
        return files
    
    def _create_fallback_files(self, scraped_data: Dict[str, Any], generated_text: str = "") -> Dict[str, str]:
        """Create fallback files using actual scraped data"""
        
        # Extract data with fallbacks
        title = scraped_data.get('title', 'Website Clone')
        meta_description = scraped_data.get('meta_description', 'AI-generated website clone')
        text_content = scraped_data.get('text_content', '').strip()
        colors = scraped_data.get('colors', ['#333333', '#ffffff', '#007bff'])
        fonts = scraped_data.get('fonts', ['Arial, sans-serif'])
        
        # Process navigation
        nav_html = self._generate_nav_from_scraped_data(scraped_data)
        
        # Process main content sections
        content_sections = self._generate_content_sections(scraped_data)
        
        # Process forms
        forms_html = self._generate_forms_html(scraped_data)
        
        # Process images
        images_html = self._generate_images_html(scraped_data)
        
        # Generate color palette for CSS
        primary_color = colors[0] if colors else '#333333'
        secondary_color = colors[1] if len(colors) > 1 else '#ffffff'
        accent_color = colors[2] if len(colors) > 2 else '#007bff'
        
        # Generate font stack
        font_family = fonts[0] if fonts else 'Arial, sans-serif'
        
        # Create enhanced HTML
        html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{meta_description}">
    <link rel="stylesheet" href="styles.css">
    {self._generate_favicon_links(scraped_data)}
</head>
<body>
    {nav_html}
    
    <main>
        {content_sections}
        {images_html}
        {forms_html}
    </main>
    
    {self._generate_footer_html(scraped_data)}
    
    <script src="script.js"></script>
</body>
</html>'''
        
        # Create enhanced CSS
        css_content = f'''/* Website Clone Styles - Generated from scraped data */
:root {{
    --primary-color: {primary_color};
    --secondary-color: {secondary_color};
    --accent-color: {accent_color};
    --font-family: {font_family};
    --text-color: #333;
    --bg-color: #fff;
    --border-radius: 8px;
    --shadow: 0 2px 10px rgba(0,0,0,0.1);
}}

* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

body {{
    font-family: var(--font-family);
    line-height: 1.6;
    color: var(--text-color);
    background-color: var(--bg-color);
}}

/* Navigation Styles */
header {{
    background: var(--primary-color);
    color: var(--secondary-color);
    padding: 1rem 0;
    box-shadow: var(--shadow);
    position: sticky;
    top: 0;
    z-index: 100;
}}

.nav-container {{
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 1rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}}

.logo {{
    font-size: 1.5rem;
    font-weight: bold;
}}

nav ul {{
    list-style: none;
    display: flex;
    gap: 2rem;
}}

nav a {{
    color: var(--secondary-color);
    text-decoration: none;
    transition: color 0.3s ease;
}}

nav a:hover {{
    color: var(--accent-color);
}}

/* Main Content */
main {{
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem 1rem;
}}

.content-section {{
    margin-bottom: 3rem;
    padding: 2rem;
    background: var(--bg-color);
    border-radius: var(--border-radius);
    box-shadow: var(--shadow);
}}

.content-section h1,
.content-section h2,
.content-section h3 {{
    color: var(--primary-color);
    margin-bottom: 1rem;
}}

.content-section h1 {{
    font-size: 2.5rem;
    border-bottom: 3px solid var(--accent-color);
    padding-bottom: 0.5rem;
}}

.content-section h2 {{
    font-size: 2rem;
}}

.content-section h3 {{
    font-size: 1.5rem;
}}

.content-section p {{
    margin-bottom: 1rem;
    text-align: justify;
}}

/* Images */
.image-gallery {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1rem;
    margin: 2rem 0;
}}

.image-item {{
    border-radius: var(--border-radius);
    overflow: hidden;
    box-shadow: var(--shadow);
}}

.image-item img {{
    width: 100%;
    height: 200px;
    object-fit: cover;
    transition: transform 0.3s ease;
}}

.image-item:hover img {{
    transform: scale(1.05);
}}

/* Forms */
.form-container {{
    background: #f8f9fa;
    padding: 2rem;
    border-radius: var(--border-radius);
    margin: 2rem 0;
}}

.form-group {{
    margin-bottom: 1rem;
}}

.form-group label {{
    display: block;
    margin-bottom: 0.5rem;
    font-weight: bold;
    color: var(--primary-color);
}}

.form-group input,
.form-group textarea,
.form-group select {{
    width: 100%;
    padding: 0.75rem;
    border: 2px solid #ddd;
    border-radius: var(--border-radius);
    font-family: inherit;
    transition: border-color 0.3s ease;
}}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {{
    outline: none;
    border-color: var(--accent-color);
}}

.btn {{
    background: var(--accent-color);
    color: white;
    padding: 0.75rem 2rem;
    border: none;
    border-radius: var(--border-radius);
    cursor: pointer;
    font-size: 1rem;
    transition: background-color 0.3s ease;
}}

.btn:hover {{
    background: color-mix(in srgb, var(--accent-color) 80%, black);
}}

/* Footer */
footer {{
    background: var(--primary-color);
    color: var(--secondary-color);
    text-align: center;
    padding: 2rem 1rem;
    margin-top: 3rem;
}}

/* Responsive Design */
@media (max-width: 768px) {{
    .nav-container {{
        flex-direction: column;
        gap: 1rem;
    }}
    
    nav ul {{
        flex-direction: column;
        text-align: center;
        gap: 1rem;
    }}
    
    .content-section {{
        padding: 1rem;
    }}
    
    .content-section h1 {{
        font-size: 2rem;
    }}
    
    .image-gallery {{
        grid-template-columns: 1fr;
    }}
}}

/* Additional color variants based on scraped palette */
{self._generate_color_variants(colors)}
'''
        
        # Create enhanced JavaScript
        js_content = f'''// Enhanced Website Clone JavaScript - Generated from scraped data
document.addEventListener('DOMContentLoaded', function() {{
    console.log('Enhanced website clone loaded successfully');
    
    // Smooth scrolling for navigation links
    const navLinks = document.querySelectorAll('nav a[href^="#"]');
    navLinks.forEach(link => {{
        link.addEventListener('click', function(e) {{
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {{
                target.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
            }}
        }});
    }});
    
    // Form handling
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {{
        form.addEventListener('submit', function(e) {{
            e.preventDefault();
            const formData = new FormData(this);
            console.log('Form submitted with data:', Object.fromEntries(formData));
            
            // Show success message
            const successMsg = document.createElement('div');
            successMsg.className = 'alert alert-success';
            successMsg.innerHTML = '<p>Form submitted successfully!</p>';
            successMsg.style.cssText = `
                background: #d4edda;
                border: 1px solid #c3e6cb;
                color: #155724;
                padding: 1rem;
                border-radius: 8px;
                margin: 1rem 0;
            `;
            
            this.parentNode.insertBefore(successMsg, this.nextSibling);
            setTimeout(() => successMsg.remove(), 5000);
        }});
    }});
    
    // Image lazy loading and lightbox effect
    const images = document.querySelectorAll('.image-item img');
    images.forEach(img => {{
        img.addEventListener('click', function() {{
            const lightbox = document.createElement('div');
            lightbox.className = 'lightbox';
            lightbox.innerHTML = `
                <div class="lightbox-content">
                    <img src="${{this.src}}" alt="${{this.alt}}">
                    <span class="close">&times;</span>
                </div>
            `;
            lightbox.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0,0,0,0.8);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 1000;
                cursor: pointer;
            `;
            
            const content = lightbox.querySelector('.lightbox-content');
            content.style.cssText = `
                position: relative;
                max-width: 90%;
                max-height: 90%;
            `;
            
            const img = lightbox.querySelector('img');
            img.style.cssText = `
                width: 100%;
                height: auto;
                border-radius: 8px;
            `;
            
            const closeBtn = lightbox.querySelector('.close');
            closeBtn.style.cssText = `
                position: absolute;
                top: -10px;
                right: -10px;
                background: white;
                color: black;
                border: none;
                border-radius: 50%;
                width: 30px;
                height: 30px;
                cursor: pointer;
                font-size: 18px;
                display: flex;
                align-items: center;
                justify-content: center;
            `;
            
            document.body.appendChild(lightbox);
            
            lightbox.addEventListener('click', function(e) {{
                if (e.target === lightbox || e.target === closeBtn) {{
                    document.body.removeChild(lightbox);
                }}
            }});
        }});
    }});
    
    // Add scroll animations
    const observerOptions = {{
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    }};
    
    const observer = new IntersectionObserver(function(entries) {{
        entries.forEach(entry => {{
            if (entry.isIntersecting) {{
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }}
        }});
    }}, observerOptions);
    
    // Observe content sections
    const sections = document.querySelectorAll('.content-section');
    sections.forEach(section => {{
        section.style.opacity = '0';
        section.style.transform = 'translateY(20px)';
        section.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(section);
    }});
    
    // Dynamic year in footer
    const yearElements = document.querySelectorAll('.current-year');
    yearElements.forEach(el => {{
        el.textContent = new Date().getFullYear();
    }});
    
    {self._generate_dynamic_js_features(scraped_data)}
}});

// Additional utility functions
function debounce(func, wait) {{
    let timeout;
    return function executedFunction(...args) {{
        const later = () => {{
            clearTimeout(timeout);
            func(...args);
        }};
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    }};
}}

// Search functionality if forms are present
{self._generate_search_functionality(scraped_data)}
'''
        
        # Create comprehensive README
        readme_content = f'''# {title} - AI Generated Clone

This is an AI-generated clone based on scraped website data.

## 📋 Original Website Analysis

- **URL**: {scraped_data.get('url', 'N/A')}
- **Title**: {title}
- **Description**: {meta_description}
- **Word Count**: {scraped_data.get('word_count', 0):,} words
- **Images**: {len(scraped_data.get('images', []))} found
- **Forms**: {len(scraped_data.get('forms', []))} found
- **Navigation Elements**: {len(scraped_data.get('navigation', {}).get('nav_elements', []))} found

## 🎨 Design Elements Extracted

### Color Palette
{self._format_color_list(colors)}

### Typography
{self._format_font_list(fonts)}

### Structure
- **Headings**: {len(scraped_data.get('structure', {}).get('headings', []))} found
- **Semantic Elements**: {len(scraped_data.get('structure', {}).get('semantic_elements', []))} found
- **Responsive Design**: {'Yes' if scraped_data.get('responsive_breakpoints', {}).get('is_responsive') else 'No'}

## 📁 Files Included

- `index.html` - Main HTML structure with actual content from scraped data
- `styles.css` - CSS styling using extracted colors and fonts
- `script.js` - JavaScript functionality with form handling and interactions
- `README.md` - This documentation file

## 🚀 Setup Instructions

1. **Local Development**
```bash
# Simply open in browser
open index.html

# Or use a local server
python -m http.server 8000
# Then visit http://localhost:8000
```

2. **Deployment Options**
- **Netlify**: Drag and drop all files to netlify.com/drop
- **Vercel**: Use `vercel --prod` command
- **GitHub Pages**: Push to repository and enable GitHub Pages
- **Any Static Host**: Upload all files to your hosting provider

## 🔧 Customization Guide

### Content Updates
- Edit `index.html` to modify text content and structure
- Replace placeholder images with your own assets
- Update navigation links in the header section

### Styling Changes
- Modify CSS variables in `styles.css` for quick color/font changes:
```css
:root {{
    --primary-color: {primary_color};
    --secondary-color: {secondary_color};
    --accent-color: {accent_color};
    --font-family: {font_family};
}}
```

### Adding Functionality
- Extend `script.js` for additional interactive features
- Form submissions are handled with console logging (connect to your backend)
- Image lightbox functionality is included

## 📱 Features Included

- ✅ Responsive design (mobile-first approach)
- ✅ Smooth scrolling navigation
- ✅ Form handling with validation
- ✅ Image lightbox gallery
- ✅ Scroll animations
- ✅ Cross-browser compatibility
- ✅ SEO-optimized markup
- ✅ Accessibility features

## 🛠 Technical Details

- **Framework**: Vanilla HTML5, CSS3, JavaScript (ES6+)
- **CSS Features**: Grid, Flexbox, CSS Variables, Media Queries
- **JavaScript Features**: Event Delegation, Intersection Observer, Form API
- **Browser Support**: Modern browsers (Chrome, Firefox, Safari, Edge)

## 📊 Performance Optimizations

- Minimal external dependencies
- Optimized CSS with efficient selectors
- Lazy loading for images
- Debounced scroll events
- Efficient DOM manipulation

## 🔗 Integration Tips

### Backend Integration
```javascript
// Replace form handling in script.js
form.addEventListener('submit', async function(e) {{
    e.preventDefault();
    const formData = new FormData(this);
    
    try {{
        const response = await fetch('/api/submit', {{
            method: 'POST',
            body: formData
        }});
        const result = await response.json();
        // Handle response
    }} catch (error) {{
        console.error('Submission error:', error);
    }}
}});
```

### CMS Integration
- Content sections are clearly marked with semantic classes
- Easy to convert to template files (PHP, JSX, etc.)
- Structured markup ready for dynamic content

## 📝 Generated Content Note

This clone contains AI-generated placeholder content based on the original website's structure and theme. Replace with your actual content as needed.

## 🆘 Support

For issues or questions about this generated clone:
1. Check browser console for JavaScript errors
2. Validate HTML/CSS using online validators
3. Test responsive design using browser dev tools
4. Ensure all file paths are correct

---

*Generated by Orchids Website Cloner - AI-Powered Website Cloning*
'''
        
        return {
            'index.html': html_content,
            'styles.css': css_content,
            'script.js': js_content,
            'README.md': readme_content
        }

    def _generate_nav_from_scraped_data(self, scraped_data: Dict[str, Any]) -> str:
        """Generate navigation HTML from scraped navigation data"""
        nav_data = scraped_data.get('navigation', {})
        nav_elements = nav_data.get('nav_elements', [])
        title = scraped_data.get('title', 'Website Clone')
        
        if not nav_elements:
            # Create basic navigation
            return f'''<header>
        <div class="nav-container">
            <div class="logo">{title}</div>
            <nav>
                <ul>
                    <li><a href="#home">Home</a></li>
                    <li><a href="#about">About</a></li>
                    <li><a href="#services">Services</a></li>
                    <li><a href="#contact">Contact</a></li>
                </ul>
            </nav>
        </div>
    </header>'''
        
        # Use actual navigation data
        nav_links = []
        for nav_element in nav_elements[:1]:  # Use first navigation element
            links = nav_element.get('links', [])
            for link in links[:8]:  # Limit to 8 links
                text = link.get('text', '').strip()
                href = link.get('href', '#')
                if text and len(text) < 50:  # Reasonable link text length
                    nav_links.append(f'<li><a href="{href}">{text}</a></li>')
        
        if not nav_links:
            nav_links = ['<li><a href="#home">Home</a></li>', '<li><a href="#about">About</a></li>']
        
        return f'''<header>
        <div class="nav-container">
            <div class="logo">{title}</div>
            <nav>
                <ul>
                    {''.join(nav_links)}
                </ul>
            </nav>
        </div>
    </header>'''

    def _generate_content_sections(self, scraped_data: Dict[str, Any]) -> str:
        """Generate main content sections from scraped data"""
        text_content = scraped_data.get('text_content', '').strip()
        headings = scraped_data.get('structure', {}).get('headings', [])
        title = scraped_data.get('title', 'Welcome')
        
        sections_html = f'''<section class="content-section" id="home">
        <h1>{title}</h1>
        <p>{scraped_data.get('meta_description', 'Welcome to our website clone generated using AI technology.')}</p>
    </section>'''
        
        if text_content and len(text_content) > 100:
            # Split content into paragraphs
            paragraphs = [p.strip() for p in text_content.split('\n') if p.strip() and len(p.strip()) > 50]
            
            # Create sections based on headings
            section_count = 0
            
            for i, heading in enumerate(headings[:6]):  # Limit to 6 headings
                heading_text = heading.get('text', '').strip()
                heading_level = heading.get('level', 2)
                
                if heading_text and len(heading_text) < 100:
                    section_count += 1
                    section_id = f"section-{section_count}"
                    
                    # Get some paragraphs for this section
                    start_idx = i * 2
                    end_idx = start_idx + 3
                    section_paragraphs = paragraphs[start_idx:end_idx]
                    
                    if not section_paragraphs and paragraphs:
                        section_paragraphs = [paragraphs[i % len(paragraphs)]]
                    
                    paragraphs_html = ''.join(f'<p>{p[:500]}{"..." if len(p) > 500 else ""}</p>' 
                                            for p in section_paragraphs)
                    
                    sections_html += f'''
    <section class="content-section" id="{section_id}">
        <h{heading_level}>{heading_text}</h{heading_level}>
        {paragraphs_html if paragraphs_html else '<p>Content section with relevant information.</p>'}
    </section>'''
        
        # If no good sections created, create default sections with content
        if section_count == 0 and text_content:
            content_chunks = [text_content[i:i+800] for i in range(0, min(len(text_content), 2400), 800)]
            
            for i, chunk in enumerate(content_chunks[:3]):
                sections_html += f'''
    <section class="content-section" id="content-{i+1}">
        <h2>Section {i+1}</h2>
        <p>{chunk}{"..." if len(chunk) == 800 else ""}</p>
    </section>'''
        
        return sections_html

    def _generate_forms_html(self, scraped_data: Dict[str, Any]) -> str:
        """Generate forms HTML from scraped form data"""
        forms = scraped_data.get('forms', [])
        
        if not forms:
            return '''
    <section class="content-section" id="contact">
        <h2>Contact Us</h2>
        <div class="form-container">
            <form>
                <div class="form-group">
                    <label for="name">Name</label>
                    <input type="text" id="name" name="name" required>
                </div>
                <div class="form-group">
                    <label for="email">Email</label>
                    <input type="email" id="email" name="email" required>
                </div>
                <div class="form-group">
                    <label for="message">Message</label>
                    <textarea id="message" name="message" rows="5" required></textarea>
                </div>
                <button type="submit" class="btn">Send Message</button>
            </form>
        </div>
    </section>'''
        
        forms_html = ""
        for i, form in enumerate(forms[:2]):  # Limit to 2 forms
            form_fields = []
            fields = form.get('fields', [])
            
            for field in fields[:8]:  # Limit to 8 fields per form
                field_name = field.get('name', f'field_{len(form_fields)}')
                field_type = field.get('type', 'text')
                field_id = field.get('id', field_name)
                field_placeholder = field.get('placeholder', '')
                field_required = field.get('required', False)
                
                # Clean field name for label
                label_text = field_name.replace('_', ' ').replace('-', ' ').title()
                
                if field.get('tag') == 'textarea':
                    form_fields.append(f'''
                <div class="form-group">
                    <label for="{field_id}">{label_text}</label>
                    <textarea id="{field_id}" name="{field_name}" placeholder="{field_placeholder}" {"required" if field_required else ""}></textarea>
                </div>''')
                elif field.get('tag') == 'select' and field.get('options'):
                    options_html = ''.join(f'<option value="{opt.get("value", "")}">{opt.get("text", "")}</option>' 
                                         for opt in field.get('options', [])[:10])
                    form_fields.append(f'''
                <div class="form-group">
                    <label for="{field_id}">{label_text}</label>
                    <select id="{field_id}" name="{field_name}" {"required" if field_required else ""}>
                        {options_html}
                    </select>
                </div>''')
                else:
                    # Regular input field
                    input_type = field_type if field_type in ['text', 'email', 'tel', 'url', 'number', 'password'] else 'text'
                    form_fields.append(f'''
                <div class="form-group">
                    <label for="{field_id}">{label_text}</label>
                    <input type="{input_type}" id="{field_id}" name="{field_name}" placeholder="{field_placeholder}" {"required" if field_required else ""}>
                </div>''')
            
            if not form_fields:
                continue
            
            form_method = form.get('method', 'post').lower()
            form_action = form.get('action', '#')
            
            forms_html += f'''
    <section class="content-section" id="form-{i+1}">
        <h2>Form {i+1}</h2>
        <div class="form-container">
            <form method="{form_method}" action="{form_action}">
                {''.join(form_fields)}
                <button type="submit" class="btn">Submit</button>
            </form>
        </div>
    </section>'''
        
        return forms_html

    def _generate_images_html(self, scraped_data: Dict[str, Any]) -> str:
        """Generate images HTML from scraped image data"""
        images = scraped_data.get('images', [])
        
        if not images:
            return ""
        
        # Filter valid images
        valid_images = []
        for img in images[:12]:  # Limit to 12 images
            src = img.get('src', '')
            alt = img.get('alt', 'Image')
            if src and src.startswith(('http://', 'https://', 'data:')):
                valid_images.append({
                    'src': src,
                    'alt': alt or 'Website Image',
                    'title': img.get('title', ''),
                    'width': img.get('width', ''),
                    'height': img.get('height', '')
                })
        
        if not valid_images:
            return ""
        
        images_html = '''
    <section class="content-section" id="gallery">
        <h2>Image Gallery</h2>
        <div class="image-gallery">'''
        
        for img in valid_images:
            images_html += f'''
            <div class="image-item">
                <img src="{img['src']}" alt="{img['alt']}" title="{img['title']}" loading="lazy">
            </div>'''
        
        images_html += '''
        </div>
    </section>'''
        
        return images_html

    def _generate_footer_html(self, scraped_data: Dict[str, Any]) -> str:
        """Generate footer HTML"""
        title = scraped_data.get('title', 'Website Clone')
        social_links = scraped_data.get('social_media', {}).get('social_links', [])
        
        social_html = ""
        if social_links:
            social_html = "<div class='social-links'>"
            for link in social_links[:5]:  # Limit to 5 social links
                platform = link.get('platform', '').title()
                url = link.get('url', '#')
                social_html += f'<a href="{url}" target="_blank">{platform}</a> '
            social_html += "</div>"
        
        return f'''<footer>
        <div class="footer-content">
            <p>&copy; <span class="current-year">2024</span> {title}. All rights reserved.</p>
            <p>AI-generated website clone based on original content.</p>
            {social_html}
        </div>
    </footer>'''

    def _generate_color_variants(self, colors: List[str]) -> str:
        """Generate additional CSS color variants"""
        if len(colors) < 4:
            return ""
        
        variants = ""
        for i, color in enumerate(colors[3:8]):  # Additional colors
            variants += f'''
.accent-{i+1} {{
    color: {color};
}}

.bg-accent-{i+1} {{
    background-color: {color};
}}
'''
        return variants

    def _format_color_list(self, colors: List[str]) -> str:
        """Format color list for README"""
        if not colors:
            return "- Default color palette used"
        
        formatted = ""
        for i, color in enumerate(colors[:8]):
            formatted += f"- Color {i+1}: `{color}`\n"
        return formatted.strip()

    def _format_font_list(self, fonts: List[str]) -> str:
        """Format font list for README"""
        if not fonts:
            return "- Arial, sans-serif (default)"
        
        formatted = ""
        for i, font in enumerate(fonts[:5]):
            formatted += f"- Font {i+1}: `{font}`\n"
        return formatted.strip()

    def _generate_favicon_links(self, scraped_data: Dict[str, Any]) -> str:
        """Generate favicon links from scraped data"""
        favicon_data = scraped_data.get('favicon', {})
        
        if not favicon_data:
            return '<link rel="icon" type="image/x-icon" href="/favicon.ico">'
        
        favicon_html = ""
        for rel, info in favicon_data.items():
            href = info.get('href', '')
            sizes = info.get('sizes', '')
            file_type = info.get('type', '')
            
            if href:
                size_attr = f' sizes="{sizes}"' if sizes else ''
                type_attr = f' type="{file_type}"' if file_type else ''
                favicon_html += f'<link rel="{rel}" href="{href}"{size_attr}{type_attr}>\n    '
        
        return favicon_html.strip()

    def _generate_dynamic_js_features(self, scraped_data: Dict[str, Any]) -> str:
        """Generate dynamic JavaScript features based on scraped data"""
        features = []
        
        # Analytics tracking if found
        analytics = scraped_data.get('analytics', {})
        if any(analytics.values()):
            features.append('''
    // Analytics placeholder - replace with actual tracking codes
    console.log('Analytics tracking initialized');''')
        
        # Search functionality if multiple content sections
        headings = scraped_data.get('structure', {}).get('headings', [])
        if len(headings) > 3:
            features.append('''
    // Simple content search
    const searchInput = document.getElementById('search');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(function(e) {
            const query = e.target.value.toLowerCase();
            const sections = document.querySelectorAll('.content-section');
            
            sections.forEach(section => {
                const text = section.textContent.toLowerCase();
                section.style.display = text.includes(query) ? 'block' : 'none';
            });
        }, 300));
    }''')
        
        # Dynamic navigation highlighting
        if len(headings) > 2:
            features.append('''
    // Navigation highlighting
    const sections = document.querySelectorAll('.content-section[id]');
    const navLinks = document.querySelectorAll('nav a[href^="#"]');
    
    const highlightNav = debounce(() => {
        let current = '';
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;
            if (scrollY >= sectionTop - 200) {
                current = section.getAttribute('id');
            }
        });
        
        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === '#' + current) {
                link.classList.add('active');
            }
        });
    }, 10);
    
    window.addEventListener('scroll', highlightNav);''')
        
        return '\n'.join(features)

    def _generate_search_functionality(self, scraped_data: Dict[str, Any]) -> str:
        """Generate search functionality if forms contain search fields"""
        forms = scraped_data.get('forms', [])
        has_search = any(
            any(field.get('type') == 'search' or 'search' in field.get('name', '').lower() 
                for field in form.get('fields', []))
            for form in forms
        )
        
        if not has_search:
            return ""
        
        return '''
// Enhanced search functionality
function initializeSearch() {
    const searchForms = document.querySelectorAll('form');
    searchForms.forEach(form => {
        const searchInputs = form.querySelectorAll('input[type="search"], input[name*="search"]');
        searchInputs.forEach(input => {
            input.addEventListener('input', debounce(function(e) {
                const query = e.target.value.toLowerCase().trim();
                if (query.length > 2) {
                    performSearch(query);
                } else {
                    clearSearchResults();
                }
            }, 300));
        });
    });
}

function performSearch(query) {
    const searchableElements = document.querySelectorAll('.content-section, .image-item');
    const results = [];
    
    searchableElements.forEach((element, index) => {
        const text = element.textContent.toLowerCase();
        const alt = element.querySelector('img')?.alt?.toLowerCase() || '';
        
        if (text.includes(query) || alt.includes(query)) {
            results.push(element);
            element.style.display = '';
            element.style.backgroundColor = '#fff3cd';
        } else {
            element.style.display = 'none';
        }
    });
    
    console.log(`Search for "${query}" found ${results.length} results`);
}

function clearSearchResults() {
    const allElements = document.querySelectorAll('.content-section, .image-item');
    allElements.forEach(element => {
        element.style.display = '';
        element.style.backgroundColor = '';
    });
}

// Initialize search on load
initializeSearch();'''
    
    def _summarize_structure(self, scraped_data: Dict[str, Any]) -> str:
        """Summarize the website structure"""
        structure = scraped_data.get('structure', {})
        headings = structure.get('headings', [])
        semantic_elements = structure.get('semantic_elements', [])
        
        summary = f"Headings: {len(headings)} found\n"
        summary += f"Semantic elements: {len(semantic_elements)} found\n"
        
        if headings:
            summary += "Heading hierarchy: "
            for h in headings[:5]:  # First 5 headings
                summary += f"H{h.get('level')} '{h.get('text', '')[:30]}', "
            summary = summary.rstrip(', ') + "\n"
        
        if semantic_elements:
            summary += "Semantic tags: "
            tags = [el.get('tag') for el in semantic_elements]
            summary += ', '.join(set(tags))
        
        return summary
    
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
        count += len(scraped_data.get('links', []))
        count += len(scraped_data.get('forms', []))
        count += len(scraped_data.get('structure', {}).get('headings', []))
        return count
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _organize_generated_files(self, generated_code: Dict[str, str]) -> Dict[str, Any]:
        """Organize generated files with metadata"""
        files = {}
        
        for filename, content in generated_code.items():
            files[filename] = {
                'content': content,
                'size': len(content),
                'type': self._get_file_type(filename),
                'description': self._get_file_description(filename)
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
        """Get file description"""
        descriptions = {
            'index.html': 'Main HTML structure and content',
            'styles.css': 'CSS styling and responsive design',
            'script.js': 'JavaScript functionality and interactions',
            'README.md': 'Setup instructions and documentation'
        }
        return descriptions.get(filename, 'Generated file')
    
    def _create_deployment_instructions(self) -> Dict[str, str]:
        """Create deployment instructions"""
        return {
            'local_development': 'Open index.html in a web browser or use a local server',
            'static_hosting': 'Upload all files to any static hosting service (Netlify, Vercel, GitHub Pages)',
            'customization': 'Edit the files to customize content, styling, and functionality',
            'requirements': 'No build process required - pure HTML/CSS/JS'
        }

    def create_style_variations(self, base_code: Dict[str, str]) -> Dict[str, Dict[str, str]]:
        """
        Create different style variations of the generated code
        """
        variations = {
            'modern': self._apply_modern_styling(base_code),
            'minimal': self._apply_minimal_styling(base_code),
            'classic': self._apply_classic_styling(base_code),
            'dark': self._apply_dark_theme(base_code)
        }
        
        return variations
    
    def _apply_modern_styling(self, base_code: Dict[str, str]) -> Dict[str, str]:
        """Apply modern styling variations"""
        # This would modify the CSS to use modern design patterns
        modified_code = base_code.copy()
        # Add modern CSS modifications here
        return modified_code
    
    def _apply_minimal_styling(self, base_code: Dict[str, str]) -> Dict[str, str]:
        """Apply minimal styling variations"""
        modified_code = base_code.copy()
        # Add minimal design modifications here
        return modified_code
    
    def _apply_classic_styling(self, base_code: Dict[str, str]) -> Dict[str, str]:
        """Apply classic styling variations"""
        modified_code = base_code.copy()
        # Add classic design modifications here
        return modified_code
    
    def _apply_dark_theme(self, base_code: Dict[str, str]) -> Dict[str, str]:
        """Apply dark theme variations"""
        modified_code = base_code.copy()
        # Add dark theme modifications here
        return modified_code