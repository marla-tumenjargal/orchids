# llm_cloner.py - AI-Powered Website Cloning

import os
from typing import Dict, Any, List
import json
import logging
from anthropic import Anthropic
from .utils import measure_performance, retry_async, setup_logging

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
        Use AI to generate a clone of the website based on scraped data
        """
        logger.info(f"Starting AI cloning process for {original_url}")
        
        try:
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
            <p>This is a cloned website created using AI.</p>
        </section>
    </main>
    
    <footer>
        <p>&copy; 2024 Website Clone</p>
    </footer>
    
    <script src="script.js"></script>
</body>
</html>''',
            'styles.css': '''* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: Arial, sans-serif;
    line-height: 1.6;
    color: #333;
}

header {
    background: #333;
    color: #fff;
    padding: 1rem;
}

nav ul {
    list-style: none;
    display: flex;
    gap: 1rem;
}

nav a {
    color: #fff;
    text-decoration: none;
}

main {
    padding: 2rem;
}

footer {
    background: #333;
    color: #fff;
    text-align: center;
    padding: 1rem;
}''',
            'script.js': '''// Website Clone JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('Website clone loaded successfully');
    
    // Add smooth scrolling for navigation links
    const navLinks = document.querySelectorAll('nav a[href^="#"]');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
});''',
            'README.md': '''# Website Clone

This is an AI-generated clone of a website.

## Setup Instructions

1. Download all files to a folder
2. Open `index.html` in a web browser
3. Customize the content as needed

## Files Included

- `index.html` - Main HTML structure
- `styles.css` - CSS styling
- `script.js` - JavaScript functionality
- `README.md` - This file

## Customization

You can modify the content, colors, and layout by editing the respective files.
'''
        }
    
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

    async def generate_enhanced_clone(self, scraped_data: Dict[str, Any], original_url: str, 
                                    user_preferences: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate an enhanced clone with user preferences
        """
        preferences = user_preferences or {}
        
        # Create enhanced prompt with preferences
        enhanced_prompt = self._create_enhanced_prompt(scraped_data, original_url, preferences)
        
        # Generate enhanced code
        enhanced_code = await self._generate_code(enhanced_prompt)
        
        return {
            'original_url': original_url,
            'enhanced_code': enhanced_code,
            'preferences_applied': preferences,
            'files': self._organize_generated_files(enhanced_code)
        }
    
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
        
        if preference_text:
            enhanced_prompt = base_prompt + f"\n\nADDITIONAL USER PREFERENCES:\n{preference_text}"
        else:
            enhanced_prompt = base_prompt
        
        return enhanced_prompt

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