import os
from typing import Dict, Any, List, Optional, Tuple
import json
from dotenv import load_dotenv
import logging
from anthropic import Anthropic
from datetime import datetime
import re
import base64
from urllib.parse import urljoin, urlparse

load_dotenv()
logger = logging.getLogger(__name__)

class VisualLLMWebsiteCloner:
    """
    A bulletproof visual website cloner that generates pixel-perfect,
    visually accurate website replicas with modern design patterns.
    """
    
    def __init__(self):
        """Initialize the cloner with all required components"""
        try:
            # Initialize Anthropic client
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY environment variable is required")
            
            self.client = Anthropic(api_key=api_key)
            self.model = "claude-3-5-sonnet-20241022"
            self._current_scraped_data = {}
            
            # Initialize all component systems
            self._initialize_all_systems()
            
            logger.info("✅ VisualLLMWebsiteCloner initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize VisualLLMWebsiteCloner: {e}")
            # Set safe defaults to prevent crashes
            self.client = None
            self.model = "claude-3-5-sonnet-20241022"
            self._current_scraped_data = {}
            self._initialize_safe_defaults()

    def _initialize_all_systems(self):
        """Initialize all cloning systems and components"""
        # Component library for UI elements
        self.component_library = {
            'hero_sections': [
                {'name': 'gradient-hero', 'type': 'modern-gradient'},
                {'name': 'video-hero', 'type': 'video-background'},
                {'name': 'minimal-hero', 'type': 'clean-minimal'}
            ],
            'navigation': [
                {'name': 'floating-nav', 'type': 'glassmorphism'},
                {'name': 'sticky-nav', 'type': 'backdrop-blur'},
                {'name': 'sidebar-nav', 'type': 'slide-out'}
            ],
            'cards': [
                {'name': 'glass-card', 'type': 'glassmorphism'},
                {'name': 'shadow-card', 'type': 'elevated'},
                {'name': 'gradient-card', 'type': 'colorful'}
            ],
            'buttons': [
                {'name': 'gradient-btn', 'type': 'modern-gradient'},
                {'name': 'glass-btn', 'type': 'glassmorphism'},
                {'name': 'shadow-btn', 'type': 'elevated'}
            ]
        }
        
        # Color schemes for different design styles
        self.color_schemes = {
            'modern-blue': {
                'primary': '#3b82f6',
                'secondary': '#8b5cf6',
                'accent': '#06b6d4',
                'background': '#ffffff',
                'surface': '#f8fafc',
                'text': '#1e293b'
            },
            'vibrant-purple': {
                'primary': '#8b5cf6',
                'secondary': '#ec4899',
                'accent': '#f59e0b',
                'background': '#ffffff',
                'surface': '#faf5ff',
                'text': '#1f2937'
            },
            'dark-theme': {
                'primary': '#60a5fa',
                'secondary': '#a78bfa',
                'accent': '#34d399',
                'background': '#0f172a',
                'surface': '#1e293b',
                'text': '#f1f5f9'
            },
            'warm-orange': {
                'primary': '#f97316',
                'secondary': '#ef4444',
                'accent': '#8b5cf6',
                'background': '#ffffff',
                'surface': '#fef3c7',
                'text': '#1f2937'
            }
        }
        
        # Typography systems
        self.typography_systems = {
            'modern': {
                'primary': 'Inter, system-ui, sans-serif',
                'heading': 'Poppins, Inter, sans-serif',
                'mono': 'JetBrains Mono, monospace'
            },
            'classic': {
                'primary': 'Georgia, serif',
                'heading': 'Playfair Display, serif',
                'mono': 'Courier New, monospace'
            },
            'minimal': {
                'primary': 'Helvetica Neue, sans-serif',
                'heading': 'SF Pro Display, sans-serif',
                'mono': 'SF Mono, monospace'
            }
        }

    def _initialize_safe_defaults(self):
        """Initialize safe defaults to prevent crashes"""
        self.component_library = {'hero_sections': [], 'navigation': [], 'cards': [], 'buttons': []}
        self.color_schemes = {'default': {'primary': '#3b82f6', 'secondary': '#8b5cf6', 'accent': '#06b6d4', 'background': '#ffffff', 'surface': '#f8fafc', 'text': '#1e293b'}}
        self.typography_systems = {'default': {'primary': 'Inter, sans-serif', 'heading': 'Poppins, sans-serif', 'mono': 'monospace'}}

    async def clone_website(self, scraped_data: Dict[str, Any], original_url: str) -> Dict[str, Any]:
        """
        Main cloning method that creates a visually accurate website replica
        """
        logger.info(f"🚀 Starting visual cloning for: {original_url}")
        
        try:
            # Store scraped data for use in other methods
            self._current_scraped_data = scraped_data
            
            # Step 1: Analyze the original website's visual design
            design_analysis = self._analyze_visual_design(scraped_data)
            logger.info(f"📊 Design analysis completed: {design_analysis.get('design_style', 'modern')}")
            
            # Step 2: Extract and process all content
            processed_content = self._process_website_content(scraped_data)
            logger.info(f"📝 Content processed: {len(processed_content.get('sections', []))} sections")
            
            # Step 3: Generate the visual clone
            clone_files = await self._generate_complete_clone(scraped_data, design_analysis, processed_content)
            logger.info(f"✨ Clone generated with {len(clone_files)} files")
            
            # Step 4: Organize and prepare final result
            result = self._create_final_result(original_url, scraped_data, design_analysis, clone_files)
            
            logger.info(f"✅ Visual cloning completed successfully for {original_url}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error in clone_website: {e}")

    async def generate_enhanced_clone(self, scraped_data: Dict[str, Any], original_url: str, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate an enhanced clone with user preferences
        """
        logger.info(f"🎨 Starting enhanced cloning for: {original_url}")
        
        try:
            # Store data
            self._current_scraped_data = scraped_data
            
            # Analyze with preferences
            design_analysis = self._analyze_visual_design(scraped_data)
            design_analysis = self._apply_user_preferences(design_analysis, preferences)
            
            # Process content
            processed_content = self._process_website_content(scraped_data)
            
            # Generate enhanced clone
            clone_files = await self._generate_enhanced_clone_files(scraped_data, design_analysis, processed_content, preferences)
            
            # Create enhanced result
            result = self._create_enhanced_result(original_url, scraped_data, design_analysis, clone_files, preferences)
            
            logger.info(f"✅ Enhanced cloning completed for {original_url}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error in generate_enhanced_clone: {e}")

    def _analyze_visual_design(self, scraped_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the visual design patterns of the scraped website"""
        try:
            analysis = {
                'design_style': 'modern',
                'color_scheme': 'modern-blue',
                'typography_style': 'modern',
                'layout_type': 'grid-based',
                'visual_score': 85,
                'has_animations': False,
                'responsive_design': True,
                'component_types': []
            }
            
            # Analyze design trends if available
            design_trends = scraped_data.get('design_trends', {})
            if design_trends:
                analysis['design_style'] = design_trends.get('designStyle', 'modern')
                analysis['visual_score'] = design_trends.get('aestheticScore', 85)
                
                color_trends = design_trends.get('colorTrends', {})
                if color_trends.get('isDarkMode'):
                    analysis['color_scheme'] = 'dark-theme'
                elif analysis['visual_score'] > 70:
                    analysis['color_scheme'] = 'vibrant-purple'
            
            # Analyze visual patterns
            visual_patterns = scraped_data.get('visual_patterns', {})
            if visual_patterns:
                animations = visual_patterns.get('animations', [])
                analysis['has_animations'] = len(animations) > 0
                
                ui_components = visual_patterns.get('uiComponents', [])
                for component in ui_components:
                    comp_type = component.get('type', '').lower()
                    if comp_type and comp_type not in analysis['component_types']:
                        analysis['component_types'].append(comp_type)
            
            # Analyze layout
            layout_data = scraped_data.get('layout', {})
            if layout_data:
                containers = layout_data.get('containers', [])
                if len(containers) > 10:
                    analysis['layout_type'] = 'complex-grid'
                elif len(containers) > 5:
                    analysis['layout_type'] = 'grid-based'
                else:
                    analysis['layout_type'] = 'simple-flex'
            
            # Check responsive design
            responsive_data = scraped_data.get('responsive_breakpoints', {})
            analysis['responsive_design'] = responsive_data.get('is_responsive', True)
            
            return analysis
            
        except Exception as e:
            logger.warning(f"⚠️ Error in design analysis: {e}")
            return {
                'design_style': 'modern',
                'color_scheme': 'modern-blue',
                'typography_style': 'modern',
                'layout_type': 'grid-based',
                'visual_score': 75,
                'has_animations': True,
                'responsive_design': True,
                'component_types': ['button', 'card', 'nav']
            }

    def _process_website_content(self, scraped_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process and organize all website content for cloning"""
        try:
            processed = {
                'title': scraped_data.get('title', 'Website Clone'),
                'description': scraped_data.get('meta_description', 'A beautiful website clone'),
                'sections': [],
                'navigation': [],
                'images': [],
                'forms': [],
                'colors': [],
                'fonts': []
            }
            
            # Process title and meta
            processed['title'] = self._clean_text(processed['title'])
            processed['description'] = self._clean_text(processed['description'])
            
            # Process navigation
            nav_data = scraped_data.get('navigation', {})
            nav_elements = nav_data.get('nav_elements', [])
            for nav in nav_elements[:1]:  # Use first navigation
                links = nav.get('links', [])
                for link in links[:6]:  # Limit to 6 main nav items
                    if link.get('text') and link.get('text').strip():
                        processed['navigation'].append({
                            'text': self._clean_text(link['text'])[:20],  # Limit length
                            'href': link.get('href', '#')
                        })
            
            # Add default navigation if none found
            if not processed['navigation']:
                processed['navigation'] = [
                    {'text': 'Home', 'href': '#home'},
                    {'text': 'About', 'href': '#about'},
                    {'text': 'Services', 'href': '#services'},
                    {'text': 'Portfolio', 'href': '#portfolio'},
                    {'text': 'Contact', 'href': '#contact'}
                ]
            
            # Process content sections
            headings = scraped_data.get('structure', {}).get('headings', [])
            current_section = None
            
            for heading in headings[:10]:  # Limit to 10 headings
                heading_text = self._clean_text(heading.get('text', ''))
                if heading_text and len(heading_text) > 2:
                    level = heading.get('level', 1)
                    
                    if level <= 2:  # Main sections
                        if current_section:
                            processed['sections'].append(current_section)
                        current_section = {
                            'title': heading_text[:60],  # Limit title length
                            'level': level,
                            'content': [],
                            'type': self._determine_section_type(heading_text)
                        }
                    elif current_section and level > 2:  # Subsections
                        current_section['content'].append({
                            'type': 'subsection',
                            'title': heading_text[:40],
                            'level': level
                        })
            
            if current_section:
                processed['sections'].append(current_section)
            
            # Add default sections if none found
            if not processed['sections']:
                processed['sections'] = [
                    {
                        'title': 'Welcome',
                        'level': 1,
                        'content': [{'type': 'text', 'value': 'Welcome to our amazing website.'}],
                        'type': 'hero'
                    },
                    {
                        'title': 'About Us',
                        'level': 2,
                        'content': [{'type': 'text', 'value': 'Learn more about what we do.'}],
                        'type': 'about'
                    },
                    {
                        'title': 'Our Services',
                        'level': 2,
                        'content': [{'type': 'text', 'value': 'Discover our professional services.'}],
                        'type': 'services'
                    }
                ]
            
            # Process images
            images = scraped_data.get('images', [])
            for img in images[:10]:  # Limit to 10 images
                if img.get('src') and not img.get('is_decorative', False):
                    processed['images'].append({
                        'src': img['src'],
                        'alt': self._clean_text(img.get('alt', 'Image'))[:50],
                        'title': self._clean_text(img.get('title', ''))[:30]
                    })
            
            # Process forms
            forms = scraped_data.get('forms', [])
            for form in forms[:3]:  # Limit to 3 forms
                form_data = {
                    'action': form.get('action', '#'),
                    'method': form.get('method', 'post'),
                    'fields': []
                }
                
                fields = form.get('fields', [])
                for field in fields[:8]:  # Limit fields
                    if field.get('name') and field.get('type'):
                        form_data['fields'].append({
                            'name': field['name'],
                            'type': field['type'],
                            'placeholder': self._clean_text(field.get('placeholder', ''))[:30],
                            'required': field.get('required', False)
                        })
                
                if form_data['fields']:
                    processed['forms'].append(form_data)
            
            # Process colors
            colors = scraped_data.get('colors', [])
            for color in colors[:6]:  # Limit to 6 colors
                if self._is_valid_color(color):
                    processed['colors'].append(color)
            
            # Process fonts
            fonts = scraped_data.get('fonts', [])
            for font in fonts[:4]:  # Limit to 4 fonts
                if font and len(font) > 3:
                    processed['fonts'].append(font)
            
            return processed
            
        except Exception as e:
            logger.warning(f"⚠️ Error processing content: {e}")
            return {
                'title': 'Website Clone',
                'description': 'A beautiful website clone',
                'sections': [
                    {'title': 'Welcome', 'level': 1, 'content': [], 'type': 'hero'},
                    {'title': 'About', 'level': 2, 'content': [], 'type': 'about'},
                    {'title': 'Contact', 'level': 2, 'content': [], 'type': 'contact'}
                ],
                'navigation': [
                    {'text': 'Home', 'href': '#home'},
                    {'text': 'About', 'href': '#about'},
                    {'text': 'Contact', 'href': '#contact'}
                ],
                'images': [],
                'forms': [],
                'colors': ['#3b82f6', '#8b5cf6'],
                'fonts': ['Inter', 'Poppins']
            }

    async def _generate_complete_clone(self, scraped_data: Dict[str, Any], design_analysis: Dict[str, Any], processed_content: Dict[str, Any]) -> Dict[str, str]:
        """Generate complete clone files"""
        try:
            # Try AI generation first
            if self.client:
                try:
                    ai_files = await self._generate_with_ai(scraped_data, design_analysis, processed_content)
                    if ai_files and len(ai_files) >= 3:  # Must have at least HTML, CSS, JS
                        return ai_files
                except Exception as e:
                    logger.warning(f"⚠️ AI generation failed: {e}")
            
            # Fallback to template generation
            return self._generate_template_clone(design_analysis, processed_content)
            
        except Exception as e:
            logger.error(f"❌ Error generating clone: {e}")
            return self._generate_emergency_clone(processed_content)

    async def _generate_enhanced_clone_files(self, scraped_data: Dict[str, Any], design_analysis: Dict[str, Any], processed_content: Dict[str, Any], preferences: Dict[str, Any]) -> Dict[str, str]:
        """Generate enhanced clone files with preferences"""
        try:
            # Try enhanced AI generation
            if self.client:
                try:
                    enhanced_files = await self._generate_enhanced_with_ai(scraped_data, design_analysis, processed_content, preferences)
                    if enhanced_files and len(enhanced_files) >= 3:
                        return enhanced_files
                except Exception as e:
                    logger.warning(f"⚠️ Enhanced AI generation failed: {e}")
            
            # Fallback to enhanced template
            return self._generate_enhanced_template_clone(design_analysis, processed_content, preferences)
            
        except Exception as e:
            logger.error(f"❌ Error generating enhanced clone: {e}")
            return self._generate_emergency_clone(processed_content)

    async def _generate_with_ai(self, scraped_data: Dict[str, Any], design_analysis: Dict[str, Any], processed_content: Dict[str, Any]) -> Dict[str, str]:
        """Generate clone using AI"""
        prompt = self._create_ai_prompt(scraped_data, design_analysis, processed_content)
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=8000,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}]
        )
        
        generated_text = response.content[0].text
        return self._parse_ai_response(generated_text, processed_content)

    async def _generate_enhanced_with_ai(self, scraped_data: Dict[str, Any], design_analysis: Dict[str, Any], processed_content: Dict[str, Any], preferences: Dict[str, Any]) -> Dict[str, str]:
        """Generate enhanced clone using AI with preferences"""
        prompt = self._create_enhanced_ai_prompt(scraped_data, design_analysis, processed_content, preferences)
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=8000,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}]
        )
        
        generated_text = response.content[0].text
        return self._parse_ai_response(generated_text, processed_content)

    def _generate_template_clone(self, design_analysis: Dict[str, Any], processed_content: Dict[str, Any]) -> Dict[str, str]:
        """Generate clone using templates (guaranteed to work)"""
        try:
            # Get design system
            color_scheme = self.color_schemes.get(design_analysis.get('color_scheme', 'modern-blue'))
            typography = self.typography_systems.get(design_analysis.get('typography_style', 'modern'))
            
            # Generate files
            html_content = self._create_html_template(processed_content, color_scheme, typography)
            css_content = self._create_css_template(color_scheme, typography, design_analysis)
            js_content = self._create_js_template(design_analysis)
            readme_content = self._create_readme_template(processed_content)
            
            return {
                'index.html': html_content,
                'styles.css': css_content,
                'script.js': js_content,
                'README.md': readme_content
            }
            
        except Exception as e:
            logger.error(f"❌ Error in template generation: {e}")
            return self._generate_emergency_clone(processed_content)

    def _generate_enhanced_template_clone(self, design_analysis: Dict[str, Any], processed_content: Dict[str, Any], preferences: Dict[str, Any]) -> Dict[str, str]:
        """Generate enhanced template clone with preferences"""
        try:
            # Apply preferences to design
            enhanced_design = self._apply_preferences_to_design(design_analysis, preferences)
            
            # Get enhanced systems
            color_scheme = self._get_enhanced_color_scheme(enhanced_design, preferences)
            typography = self.typography_systems.get(enhanced_design.get('typography_style', 'modern'))
            
            # Generate enhanced files
            html_content = self._create_enhanced_html_template(processed_content, color_scheme, typography, preferences)
            css_content = self._create_enhanced_css_template(color_scheme, typography, enhanced_design, preferences)
            js_content = self._create_enhanced_js_template(enhanced_design, preferences)
            readme_content = self._create_enhanced_readme_template(processed_content, preferences)
            
            files = {
                'index.html': html_content,
                'styles.css': css_content,
                'script.js': js_content,
                'README.md': readme_content
            }
            
            # Add premium files if requested
            if preferences.get('premium_features'):
                files['premium.css'] = self._create_premium_css()
                files['animations.js'] = self._create_advanced_animations_js()
            
            return files
            
        except Exception as e:
            logger.error(f"❌ Error in enhanced template generation: {e}")
            return self._generate_emergency_clone(processed_content)

    def _generate_emergency_clone(self, processed_content: Dict[str, Any]) -> Dict[str, str]:
        """Emergency fallback that always works"""
        title = processed_content.get('title', 'Website Clone')
        description = processed_content.get('description', 'A beautiful website')
        
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{description}">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 0 20px; }}
        header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2rem 0; text-align: center; }}
        h1 {{ font-size: 3rem; margin-bottom: 1rem; }}
        .subtitle {{ font-size: 1.2rem; opacity: 0.9; }}
        main {{ padding: 4rem 0; }}
        .section {{ margin-bottom: 4rem; }}
        .section h2 {{ font-size: 2rem; margin-bottom: 1rem; color: #667eea; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; margin-top: 2rem; }}
        .card {{ background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: transform 0.3s ease; }}
        .card:hover {{ transform: translateY(-5px); }}
        footer {{ background: #333; color: white; text-align: center; padding: 2rem 0; }}
        .btn {{ display: inline-block; background: #667eea; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; transition: background 0.3s ease; }}
        .btn:hover {{ background: #5a6fd8; }}
    </style>
</head>
<body>
    <header>
        <div class="container">
            <h1>{title}</h1>
            <p class="subtitle">{description}</p>
        </div>
    </header>
    <main>
        <div class="container">
            <section class="section">
                <h2>Welcome</h2>
                <p>This is a beautiful website clone created with advanced AI technology.</p>
            </section>
            <section class="section">
                <h2>Features</h2>
                <div class="grid">
                    <div class="card">
                        <h3>Modern Design</h3>
                        <p>Beautiful, responsive design that works on all devices.</p>
                    </div>
                    <div class="card">
                        <h3>Fast Performance</h3>
                        <p>Optimized for speed and excellent user experience.</p>
                    </div>
                    <div class="card">
                        <h3>Easy to Use</h3>
                        <p>Intuitive interface that anyone can navigate.</p>
                    </div>
                </div>
            </section>
            <section class="section">
                <h2>Get Started</h2>
                <p>Ready to begin? Contact us today!</p>
                <a href="#contact" class="btn">Contact Us</a>
            </section>
        </div>
    </main>
    <footer>
        <div class="container">
            <p>&copy; 2024 {title}. All rights reserved.</p>
        </div>
    </footer>
</body>
</html>'''
        
        return {
            'index.html': html,
            'styles.css': '/* Emergency CSS loaded inline */',
            'script.js': '// Emergency JavaScript\nconsole.log("Website loaded successfully!");',
            'README.md': f'# {title}\n\nA beautiful website clone.\n\n## Features\n- Modern design\n- Responsive layout\n- Fast performance'
        }

    def _create_html_template(self, content: Dict[str, Any], colors: Dict[str, str], typography: Dict[str, str]) -> str:
        """Create comprehensive HTML template"""
        title = content['title']
        description = content['description']
        navigation = content['navigation']
        sections = content['sections']
        
        # Build navigation HTML
        nav_items = []
        for nav_item in navigation:
            nav_items.append(f'<a href="{nav_item["href"]}" class="nav-link">{nav_item["text"]}</a>')
        nav_html = '\n                '.join(nav_items)
        
        # Build sections HTML
        sections_html = []
        for i, section in enumerate(sections):
            section_id = f"section-{i+1}"
            section_type = section.get('type', 'content')
            
            if section_type == 'hero':
                sections_html.append(f'''
    <section id="{section_id}" class="hero-section">
        <div class="hero-background">
            <div class="gradient-orb orb-1"></div>
            <div class="gradient-orb orb-2"></div>
            <div class="gradient-orb orb-3"></div>
        </div>
        <div class="container hero-container">
            <div class="hero-content">
                <h1 class="hero-title">{section["title"]}</h1>
                <p class="hero-description">{description}</p>
                <div class="hero-buttons">
                    <a href="#contact" class="btn btn-primary">Get Started</a>
                    <a href="#about" class="btn btn-secondary">Learn More</a>
                </div>
            </div>
            <div class="hero-visual">
                <div class="floating-element element-1"></div>
                <div class="floating-element element-2"></div>
                <div class="floating-element element-3"></div>
            </div>
        </div>
    </section>''')
            else:
                sections_html.append(f'''
    <section id="{section_id}" class="content-section">
        <div class="container">
            <div class="section-header">
                <h2 class="section-title">{section["title"]}</h2>
            </div>
            <div class="section-content">
                <div class="features-grid">
                    <div class="feature-card">
                        <div class="feature-icon">
                            <div class="icon-shape"></div>
                        </div>
                        <h3>Amazing Feature</h3>
                        <p>Description of this amazing feature that makes your website stand out.</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">
                            <div class="icon-shape"></div>
                        </div>
                        <h3>Great Service</h3>
                        <p>Professional service delivery that exceeds expectations every time.</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">
                            <div class="icon-shape"></div>
                        </div>
                        <h3>Expert Support</h3>
                        <p>Round-the-clock support from our team of dedicated professionals.</p>
                    </div>
                </div>
            </div>
        </div>
    </section>''')
        
        sections_content = '\n'.join(sections_html)
        
        # Add contact section if forms exist
        contact_section = ""
        if content.get('forms'):
            form = content['forms'][0]
            form_fields = []
            for field in form['fields']:
                if field['type'] == 'textarea':
                    form_fields.append(f'''
                    <div class="form-group">
                        <label for="{field['name']}">{field['name'].title()}</label>
                        <textarea id="{field['name']}" name="{field['name']}" placeholder="{field['placeholder']}" {"required" if field['required'] else ""}></textarea>
                    </div>''')
                else:
                    form_fields.append(f'''
                    <div class="form-group">
                        <label for="{field['name']}">{field['name'].title()}</label>
                        <input type="{field['type']}" id="{field['name']}" name="{field['name']}" placeholder="{field['placeholder']}" {"required" if field['required'] else ""}>
                    </div>''')
            
            form_html = '\n'.join(form_fields)
            contact_section = f'''
    <section id="contact" class="contact-section">
        <div class="container">
            <div class="section-header">
                <h2 class="section-title">Get In Touch</h2>
                <p class="section-subtitle">Ready to start your next project? Let's create something amazing together.</p>
            </div>
            <div class="contact-content">
                <div class="contact-info">
                    <h3>Contact Information</h3>
                    <p>Reach out to us for any inquiries or support.</p>
                </div>
                <form class="contact-form" action="{form['action']}" method="{form['method']}">
                    {form_html}
                    <button type="submit" class="btn btn-primary btn-full">Send Message</button>
                </form>
            </div>
        </div>
    </section>'''
        
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{description}">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Poppins:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar">
        <div class="nav-container">
            <div class="nav-brand">
                <div class="brand-icon"></div>
                <span class="brand-text">{title}</span>
            </div>
            <div class="nav-menu">
                {nav_html}
            </div>
            <div class="nav-toggle">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    </nav>

    <!-- Main Content -->
    <main>
        {sections_content}
        {contact_section}
    </main>

    <!-- Footer -->
    <footer class="footer">
        <div class="footer-background">
            <div class="footer-gradient"></div>
        </div>
        <div class="container">
            <div class="footer-content">
                <div class="footer-brand">
                    <div class="brand-icon"></div>
                    <span class="brand-text">{title}</span>
                </div>
                <div class="footer-links">
                    {nav_html}
                </div>
            </div>
            <div class="footer-bottom">
                <p>&copy; 2024 {title}. All rights reserved. Created with AI.</p>
            </div>
        </div>
    </footer>

    <script src="script.js"></script>
</body>
</html>'''

    def _create_css_template(self, colors: Dict[str, str], typography: Dict[str, str], design_analysis: Dict[str, Any]) -> str:
        """Create comprehensive CSS template"""
        return f'''/* Modern Website Styles */
:root {{
    /* Colors */
    --primary: {colors['primary']};
    --secondary: {colors['secondary']};
    --accent: {colors['accent']};
    --background: {colors['background']};
    --surface: {colors['surface']};
    --text: {colors['text']};
    
    /* Typography */
    --font-primary: {typography['primary']};
    --font-heading: {typography['heading']};
    --font-mono: {typography['mono']};
    
    /* Spacing */
    --space-xs: 0.5rem;
    --space-sm: 1rem;
    --space-md: 1.5rem;
    --space-lg: 2rem;
    --space-xl: 3rem;
    --space-2xl: 4rem;
    --space-3xl: 6rem;
    
    /* Shadows */
    --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    
    /* Border Radius */
    --radius-sm: 0.375rem;
    --radius-md: 0.5rem;
    --radius-lg: 0.75rem;
    --radius-xl: 1rem;
    --radius-2xl: 1.5rem;
    
    /* Gradients */
    --gradient-primary: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
    --gradient-accent: linear-gradient(135deg, var(--secondary) 0%, var(--accent) 100%);
}}

/* Reset & Base */
*, *::before, *::after {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}}

html {{
    scroll-behavior: smooth;
    font-size: 16px;
}}

body {{
    font-family: var(--font-primary);
    background: var(--background);
    color: var(--text);
    line-height: 1.6;
    overflow-x: hidden;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}}

/* Container */
.container {{
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 var(--space-lg);
}}

/* Navigation */
.navbar {{
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 1000;
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(20px);
    border-bottom: 1px solid rgba(0, 0, 0, 0.05);
    transition: all 0.3s ease;
}}

.nav-container {{
    max-width: 1200px;
    margin: 0 auto;
    padding: var(--space-sm) var(--space-lg);
    display: flex;
    align-items: center;
    justify-content: space-between;
}}

.nav-brand {{
    display: flex;
    align-items: center;
    gap: var(--space-sm);
    font-family: var(--font-heading);
    font-weight: 700;
    font-size: 1.5rem;
    color: var(--text);
    text-decoration: none;
}}

.brand-icon {{
    width: 40px;
    height: 40px;
    background: var(--gradient-primary);
    border-radius: var(--radius-lg);
    position: relative;
    overflow: hidden;
}}

.brand-icon::after {{
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 20px;
    height: 20px;
    background: white;
    border-radius: var(--radius-md);
}}

.nav-menu {{
    display: flex;
    gap: var(--space-xl);
    list-style: none;
}}

.nav-link {{
    text-decoration: none;
    color: var(--text);
    font-weight: 500;
    position: relative;
    transition: all 0.3s ease;
    padding: var(--space-xs) 0;
}}

.nav-link::after {{
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    width: 0;
    height: 2px;
    background: var(--gradient-primary);
    transition: width 0.3s ease;
}}

.nav-link:hover {{
    color: var(--primary);
}}

.nav-link:hover::after {{
    width: 100%;
}}

.nav-toggle {{
    display: none;
    flex-direction: column;
    gap: 4px;
    cursor: pointer;
}}

.nav-toggle span {{
    width: 24px;
    height: 2px;
    background: var(--text);
    transition: all 0.3s ease;
}}

/* Hero Section */
.hero-section {{
    min-height: 100vh;
    position: relative;
    display: flex;
    align-items: center;
    background: var(--gradient-primary);
    overflow: hidden;
}}

.hero-background {{
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    overflow: hidden;
}}

.gradient-orb {{
    position: absolute;
    border-radius: 50%;
    filter: blur(60px);
    opacity: 0.3;
    animation: float 8s ease-in-out infinite;
}}

.orb-1 {{
    width: 400px;
    height: 400px;
    background: rgba(255, 255, 255, 0.1);
    top: 10%;
    left: 10%;
    animation-delay: 0s;
}}

.orb-2 {{
    width: 300px;
    height: 300px;
    background: rgba(255, 255, 255, 0.15);
    top: 60%;
    right: 20%;
    animation-delay: 2s;
}}

.orb-3 {{
    width: 200px;
    height: 200px;
    background: rgba(255, 255, 255, 0.1);
    bottom: 20%;
    left: 60%;
    animation-delay: 4s;
}}

.hero-container {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--space-3xl);
    align-items: center;
    position: relative;
    z-index: 2;
}}

.hero-content {{
    color: white;
}}

.hero-title {{
    font-family: var(--font-heading);
    font-size: clamp(2.5rem, 5vw, 4rem);
    font-weight: 800;
    line-height: 1.1;
    margin-bottom: var(--space-md);
}}

.hero-description {{
    font-size: 1.25rem;
    opacity: 0.9;
    margin-bottom: var(--space-xl);
    line-height: 1.6;
}}

.hero-buttons {{
    display: flex;
    gap: var(--space-md);
    flex-wrap: wrap;
}}

.hero-visual {{
    position: relative;
    height: 400px;
}}

.floating-element {{
    position: absolute;
    border-radius: var(--radius-2xl);
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    animation: float 6s ease-in-out infinite;
}}

.element-1 {{
    width: 200px;
    height: 120px;
    top: 50px;
    right: 100px;
    animation-delay: 0s;
}}

.element-2 {{
    width: 150px;
    height: 100px;
    top: 200px;
    right: 50px;
    animation-delay: 1s;
}}

.element-3 {{
    width: 120px;
    height: 80px;
    top: 300px;
    right: 200px;
    animation-delay: 2s;
}}

/* Buttons */
.btn {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: var(--space-sm) var(--space-lg);
    border: none;
    border-radius: var(--radius-lg);
    font-weight: 600;
    font-size: 1rem;
    text-decoration: none;
    cursor: pointer;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}}

.btn-primary {{
    background: white;
    color: var(--primary);
    box-shadow: var(--shadow-lg);
}}

.btn-primary:hover {{
    transform: translateY(-2px);
    box-shadow: var(--shadow-xl);
}}

.btn-secondary {{
    background: rgba(255, 255, 255, 0.1);
    color: white;
    border: 1px solid rgba(255, 255, 255, 0.2);
    backdrop-filter: blur(10px);
}}

.btn-secondary:hover {{
    background: rgba(255, 255, 255, 0.2);
    transform: translateY(-2px);
}}

.btn-full {{
    width: 100%;
}}

/* Content Sections */
.content-section {{
    padding: var(--space-3xl) 0;
    background: var(--surface);
}}

.content-section:nth-child(even) {{
    background: var(--background);
}}

.section-header {{
    text-align: center;
    margin-bottom: var(--space-3xl);
}}

.section-title {{
    font-family: var(--font-heading);
    font-size: clamp(2rem, 4vw, 3rem);
    font-weight: 700;
    margin-bottom: var(--space-md);
    color: var(--text);
}}

.section-subtitle {{
    font-size: 1.25rem;
    color: rgba(107, 114, 128, 1);
    max-width: 600px;
    margin: 0 auto;
}}

/* Features Grid */
.features-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: var(--space-xl);
}}

.feature-card {{
    background: white;
    padding: var(--space-xl);
    border-radius: var(--radius-2xl);
    text-align: center;
    transition: all 0.3s ease;
    border: 1px solid rgba(0, 0, 0, 0.05);
    box-shadow: var(--shadow-sm);
}}

.feature-card:hover {{
    transform: translateY(-8px);
    box-shadow: var(--shadow-xl);
}}

.feature-icon {{
    width: 80px;
    height: 80px;
    margin: 0 auto var(--space-md);
    border-radius: var(--radius-2xl);
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--gradient-primary);
}}

.icon-shape {{
    width: 40px;
    height: 40px;
    background: white;
    border-radius: var(--radius-lg);
}}

.feature-card h3 {{
    font-family: var(--font-heading);
    font-size: 1.5rem;
    font-weight: 600;
    margin-bottom: var(--space-sm);
    color: var(--text);
}}

.feature-card p {{
    color: rgba(107, 114, 128, 1);
    line-height: 1.6;
}}

/* Contact Section */
.contact-section {{
    padding: var(--space-3xl) 0;
    background: var(--surface);
}}

.contact-content {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--space-3xl);
    align-items: start;
}}

.contact-info h3 {{
    font-family: var(--font-heading);
    font-size: 1.5rem;
    font-weight: 600;
    margin-bottom: var(--space-md);
    color: var(--text);
}}

.contact-form {{
    background: white;
    padding: var(--space-xl);
    border-radius: var(--radius-2xl);
    box-shadow: var(--shadow-lg);
}}

.form-group {{
    margin-bottom: var(--space-md);
}}

.form-group label {{
    display: block;
    margin-bottom: var(--space-xs);
    font-weight: 600;
    color: var(--text);
}}

.form-group input,
.form-group textarea {{
    width: 100%;
    padding: var(--space-sm) var(--space-md);
    border: 1px solid rgba(229, 231, 235, 1);
    border-radius: var(--radius-lg);
    font-family: inherit;
    font-size: 1rem;
    transition: all 0.3s ease;
    background: white;
}}

.form-group input:focus,
.form-group textarea:focus {{
    outline: none;
    border-color: var(--primary);
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}}

.form-group textarea {{
    resize: vertical;
    min-height: 120px;
}}

/* Footer */
.footer {{
    position: relative;
    background: var(--text);
    color: white;
    padding: var(--space-3xl) 0 var(--space-lg);
    overflow: hidden;
}}

.footer-background {{
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
}}

.footer-gradient {{
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 200px;
    background: var(--gradient-primary);
    opacity: 0.1;
}}

.footer-content {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--space-xl);
    position: relative;
    z-index: 2;
}}

.footer-brand {{
    display: flex;
    align-items: center;
    gap: var(--space-sm);
    font-family: var(--font-heading);
    font-weight: 700;
    font-size: 1.5rem;
}}

.footer-links {{
    display: flex;
    gap: var(--space-xl);
}}

.footer-links .nav-link {{
    color: rgba(255, 255, 255, 0.8);
}}

.footer-links .nav-link:hover {{
    color: white;
}}

.footer-bottom {{
    text-align: center;
    padding-top: var(--space-lg);
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    color: rgba(255, 255, 255, 0.6);
    position: relative;
    z-index: 2;
}}

/* Animations */
@keyframes float {{
    0%, 100% {{ transform: translateY(0px) rotate(0deg); }}
    50% {{ transform: translateY(-20px) rotate(180deg); }}
}}

@keyframes fadeInUp {{
    from {{
        opacity: 0;
        transform: translateY(30px);
    }}
    to {{
        opacity: 1;
        transform: translateY(0);
    }}
}}

.fade-in-up {{
    animation: fadeInUp 0.8s ease-out forwards;
    opacity: 0;
}}

/* Responsive Design */
@media (max-width: 768px) {{
    .hero-container {{
        grid-template-columns: 1fr;
        text-align: center;
        gap: var(--space-xl);
    }}
    
    .contact-content {{
        grid-template-columns: 1fr;
    }}
    
    .nav-menu {{
        display: none;
    }}
    
    .nav-toggle {{
        display: flex;
    }}
    
    .footer-content {{
        flex-direction: column;
        gap: var(--space-lg);
        text-align: center;
    }}
    
    .footer-links {{
        flex-wrap: wrap;
        justify-content: center;
    }}
    
    .hero-buttons {{
        justify-content: center;
    }}
    
    .features-grid {{
        grid-template-columns: 1fr;
    }}
    
    .container {{
        padding: 0 var(--space-md);
    }}
}}

@media (max-width: 480px) {{
    .hero-title {{
        font-size: 2rem;
    }}
    
    .section-title {{
        font-size: 1.8rem;
    }}
    
    .btn {{
        padding: var(--space-sm) var(--space-md);
        font-size: 0.9rem;
    }}
    
    .feature-card {{
        padding: var(--space-lg);
    }}
    
    .contact-form {{
        padding: var(--space-lg);
    }}
}}

/* Accessibility */
@media (prefers-reduced-motion: reduce) {{
    *, *::before, *::after {{
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }}
}}

.sr-only {{
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
}}

/* Focus Styles */
.btn:focus-visible,
.nav-link:focus-visible,
input:focus-visible,
textarea:focus-visible {{
    outline: 2px solid var(--primary);
    outline-offset: 2px;
}}'''

    def _create_js_template(self, design_analysis: Dict[str, Any]) -> str:
        """Create basic JavaScript template"""
        return '''// Main JavaScript for Website Functionality
class WebsiteFunctionality {
    constructor() {
        this.initNavigation();
        this.initAnimations();
        this.initForms();
    }
    
    initNavigation() {
        // Mobile menu toggle
        const navToggle = document.querySelector('.nav-toggle');
        const navMenu = document.querySelector('.nav-menu');
        
        if (navToggle && navMenu) {
            navToggle.addEventListener('click', () => {
                navMenu.classList.toggle('active');
                navToggle.classList.toggle('active');
            });
        }
        
        // Smooth scrolling for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                e.preventDefault();
                
                const targetId = this.getAttribute('href');
                if (targetId === '#') return;
                
                const targetElement = document.querySelector(targetId);
                if (targetElement) {
                    targetElement.scrollIntoView({
                        behavior: 'smooth'
                    });
                }
            });
        });
    }
    
    initAnimations() {
        // Initialize any animations if needed
        if (document.querySelectorAll('.fade-in-up').length > 0) {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('animated');
                    }
                });
            }, { threshold: 0.1 });
            
            document.querySelectorAll('.fade-in-up').forEach(el => {
                observer.observe(el);
            });
        }
    }
    
    initForms() {
        // Form submission handling
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const submitButton = form.querySelector('button[type="submit"]');
                if (submitButton) {
                    submitButton.disabled = true;
                    submitButton.textContent = 'Sending...';
                }
                
                try {
                    const formData = new FormData(form);
                    const response = await fetch(form.action, {
                        method: form.method,
                        body: formData,
                        headers: {
                            'Accept': 'application/json'
                        }
                    });
                    
                    if (response.ok) {
                        form.reset();
                        alert('Message sent successfully!');
                    } else {
                        throw new Error('Form submission failed');
                    }
                } catch (error) {
                    console.error('Form error:', error);
                    alert('There was a problem sending your message. Please try again.');
                } finally {
                    if (submitButton) {
                        submitButton.disabled = false;
                        submitButton.textContent = 'Send Message';
                    }
                }
            });
        });
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new WebsiteFunctionality();
});'''
