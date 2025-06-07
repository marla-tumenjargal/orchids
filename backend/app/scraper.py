# scraper.py - Website Analysis and Content Extraction

from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
import asyncio
import base64
from bs4 import BeautifulSoup
import re
import json
from typing import Dict, Any, List, Optional, Tuple
import logging
from urllib.parse import urljoin, urlparse
import time
from .utils import measure_performance, retry_async, setup_logging

logger = logging.getLogger(__name__)

class WebsiteScraper:
    def __init__(self):
        self.browser = None
        self.page = None
        self.context = None
        self.playwright = None
        
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup()
    
    async def cleanup(self):
        """Clean up browser resources"""
        try:
            if self.page:
                await self.page.close()
                self.page = None
            if self.context:
                await self.context.close()
                self.context = None
            if self.browser:
                await self.browser.close()
                self.browser = None
            if self.playwright:
                await self.playwright.stop()
                self.playwright = None
        except Exception as e:
            logger.warning(f"Error during cleanup: {e}")

    @retry_async(max_retries=3)
    @measure_performance
    async def scrape_website(self, url: str) -> Dict[str, Any]:
        """
        Scrape a website and extract all relevant content with enhanced visual analysis
        """
        logger.info(f"Starting to scrape website: {url}")
        
        try:
            self.playwright = await async_playwright().start()
            
            # Launch browser with optimized settings
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--disable-extensions',
                    '--disable-background-timer-throttling',
                    '--disable-renderer-backgrounding',
                    '--disable-backgrounding-occluded-windows'
                ]
            )
            
            # Create context with realistic settings
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            # Create page
            self.page = await self.context.new_page()
            
            # Set additional headers
            await self.page.set_extra_http_headers({
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            })
            
            # Navigate to the page with error handling
            try:
                response = await self.page.goto(
                    url, 
                    wait_until="networkidle", 
                    timeout=30000
                )
                
                if not response or response.status >= 400:
                    raise Exception(f"Failed to load page: HTTP {response.status if response else 'Unknown'}")
                
            except PlaywrightTimeoutError:
                logger.warning(f"Network idle timeout for {url}, trying with domcontentloaded")
                await self.page.goto(url, wait_until="domcontentloaded", timeout=20000)
            
            # Wait for page to settle
            await self.page.wait_for_timeout(3000)
            
            # Handle cookie banners and popups
            await self._handle_popups()
            
            # Get page content
            html_content = await self.page.content()
            
            # Extract structured data
            scraped_data = await self._extract_page_data(url, html_content)
            
            # Enhanced visual analysis
            try:
                # Extract visual design patterns
                visual_patterns = await self._extract_visual_design_patterns()
                scraped_data['visual_patterns'] = visual_patterns
                
                # Extract media and graphics
                media_data = await self._extract_media_and_graphics()
                scraped_data['media_data'] = media_data
                
                # Analyze modern design trends
                design_trends = await self._analyze_modern_design_trends()
                scraped_data['design_trends'] = design_trends
                
                # Generate design recommendations
                scraped_data['design_recommendations'] = self._generate_design_recommendations(
                    visual_patterns, media_data, design_trends
                )
                
                logger.info(f"Enhanced visual analysis completed for {url}")
            except Exception as e:
                logger.warning(f"Error in enhanced visual analysis: {e}")
                # Continue without enhanced features
                scraped_data['visual_patterns'] = {}
                scraped_data['media_data'] = {}
                scraped_data['design_trends'] = {'designStyle': 'modern', 'aestheticScore': 50}
                scraped_data['design_recommendations'] = self._get_default_recommendations()
            
            # Take screenshots at different viewport sizes
            screenshots = await self._capture_screenshots()
            scraped_data['screenshots'] = screenshots
            
            # Get performance metrics
            performance_data = await self._get_performance_metrics()
            scraped_data['performance'] = performance_data
            
            logger.info(f"Successfully scraped {url}")
            return scraped_data
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            raise Exception(f"Failed to scrape website: {str(e)}")
        finally:
            await self.cleanup()

    async def _extract_visual_design_patterns(self) -> Dict[str, Any]:
        """Extract comprehensive visual design patterns and modern web elements"""
        if not self.page:
            return {}
        
        try:
            visual_data = await self.page.evaluate('''
                () => {
                    const visualPatterns = {
                        animations: [],
                        gradients: [],
                        shadows: [],
                        borderRadius: [],
                        layouts: {},
                        modernElements: {},
                        interactiveElements: [],
                        visualHierarchy: {},
                        designSystem: {},
                        uiComponents: []
                    };
                    
                    // Extract CSS animations and transitions
                    const styles = Array.from(document.styleSheets);
                    styles.forEach(sheet => {
                        try {
                            const rules = Array.from(sheet.cssRules || sheet.rules || []);
                            rules.forEach(rule => {
                                if (rule.style) {
                                    const cssText = rule.cssText;
                                    
                                    // Extract animations
                                    if (cssText.includes('animation') || cssText.includes('transition')) {
                                        visualPatterns.animations.push({
                                            selector: rule.selectorText,
                                            animation: rule.style.animation,
                                            transition: rule.style.transition,
                                            transform: rule.style.transform
                                        });
                                    }
                                    
                                    // Extract gradients
                                    if (cssText.includes('gradient')) {
                                        const gradientMatch = cssText.match(/(linear|radial)-gradient\\([^)]+\\)/g);
                                        if (gradientMatch) {
                                            visualPatterns.gradients.push(...gradientMatch);
                                        }
                                    }
                                    
                                    // Extract box shadows
                                    if (rule.style.boxShadow) {
                                        visualPatterns.shadows.push(rule.style.boxShadow);
                                    }
                                    
                                    // Extract border radius patterns
                                    if (rule.style.borderRadius) {
                                        visualPatterns.borderRadius.push(rule.style.borderRadius);
                                    }
                                }
                            });
                        } catch (e) {
                            // Skip inaccessible stylesheets
                        }
                    });
                    
                    // Analyze layout patterns
                    const containers = document.querySelectorAll('div, section, main, article');
                    const layoutPatterns = {
                        grid: 0,
                        flexbox: 0,
                        cards: 0,
                        hero: 0,
                        sidebar: 0,
                        masonry: 0
                    };
                    
                    containers.forEach(container => {
                        const styles = window.getComputedStyle(container);
                        
                        if (styles.display === 'grid') {
                            layoutPatterns.grid++;
                            visualPatterns.layouts.gridColumns = styles.gridTemplateColumns;
                            visualPatterns.layouts.gridGap = styles.gap;
                        }
                        
                        if (styles.display === 'flex') {
                            layoutPatterns.flexbox++;
                            visualPatterns.layouts.flexDirection = styles.flexDirection;
                            visualPatterns.layouts.justifyContent = styles.justifyContent;
                        }
                        
                        // Detect card patterns
                        if (container.className.toLowerCase().includes('card') || 
                            (styles.borderRadius && styles.boxShadow)) {
                            layoutPatterns.cards++;
                        }
                        
                        // Detect hero sections
                        if (container.className.toLowerCase().includes('hero') ||
                            (container.offsetHeight > window.innerHeight * 0.7)) {
                            layoutPatterns.hero++;
                        }
                    });
                    
                    visualPatterns.layouts.patterns = layoutPatterns;
                    
                    // Extract modern UI components
                    const modernSelectors = [
                        '.btn', '.button', '[class*="btn"]',
                        '.modal', '.popup', '.overlay',
                        '.carousel', '.slider', '.gallery',
                        '.dropdown', '.menu', '.nav',
                        '.card', '.tile', '.panel',
                        '.badge', '.chip', '.tag',
                        '.progress', '.loading', '.spinner',
                        '.tooltip', '.popover',
                        '.tabs', '.accordion',
                        '.timeline', '.stepper'
                    ];
                    
                    modernSelectors.forEach(selector => {
                        const elements = document.querySelectorAll(selector);
                        if (elements.length > 0) {
                            const sample = elements[0];
                            const styles = window.getComputedStyle(sample);
                            
                            visualPatterns.uiComponents.push({
                                type: selector.replace(/[\\.\\[\\]\\*=:"]/g, ''),
                                count: elements.length,
                                styles: {
                                    backgroundColor: styles.backgroundColor,
                                    color: styles.color,
                                    padding: styles.padding,
                                    borderRadius: styles.borderRadius,
                                    boxShadow: styles.boxShadow,
                                    border: styles.border,
                                    fontSize: styles.fontSize,
                                    fontWeight: styles.fontWeight
                                }
                            });
                        }
                    });
                    
                    // Extract interactive elements
                    const interactiveElements = document.querySelectorAll(
                        'button, a, input, [onclick], [onmouseover], [data-toggle], [data-action]'
                    );
                    
                    interactiveElements.forEach(el => {
                        const rect = el.getBoundingClientRect();
                        if (rect.width > 0 && rect.height > 0) {
                            const styles = window.getComputedStyle(el);
                            visualPatterns.interactiveElements.push({
                                tag: el.tagName,
                                className: el.className,
                                hasHover: styles.cursor === 'pointer',
                                styles: {
                                    backgroundColor: styles.backgroundColor,
                                    color: styles.color,
                                    borderRadius: styles.borderRadius,
                                    padding: styles.padding,
                                    transition: styles.transition
                                }
                            });
                        }
                    });
                    
                    // Analyze visual hierarchy
                    const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
                    const hierarchy = {};
                    
                    headings.forEach(heading => {
                        const styles = window.getComputedStyle(heading);
                        const level = heading.tagName;
                        
                        if (!hierarchy[level]) {
                            hierarchy[level] = {
                                fontSize: styles.fontSize,
                                fontWeight: styles.fontWeight,
                                color: styles.color,
                                marginBottom: styles.marginBottom,
                                lineHeight: styles.lineHeight
                            };
                        }
                    });
                    
                    visualPatterns.visualHierarchy = hierarchy;
                    
                    // Extract design system tokens
                    const rootStyles = window.getComputedStyle(document.documentElement);
                    const cssVariables = {};
                    
                    // Extract CSS custom properties
                    for (let i = 0; i < rootStyles.length; i++) {
                        const prop = rootStyles[i];
                        if (prop.startsWith('--')) {
                            cssVariables[prop] = rootStyles.getPropertyValue(prop);
                        }
                    }
                    
                    visualPatterns.designSystem = {
                        cssVariables: cssVariables,
                        spacing: {
                            small: '8px',
                            medium: '16px',
                            large: '24px',
                            xlarge: '32px'
                        }
                    };
                    
                    return visualPatterns;
                }
            ''')
            
            return visual_data
        except Exception as e:
            logger.warning(f"Error extracting visual patterns: {e}")
            return {}

    async def _extract_media_and_graphics(self) -> Dict[str, Any]:
        """Extract media elements and generate graphics data"""
        if not self.page:
            return {}
        
        try:
            media_data = await self.page.evaluate('''
                () => {
                    const mediaInfo = {
                        icons: [],
                        illustrations: [],
                        backgroundImages: [],
                        svgElements: [],
                        canvasElements: [],
                        videoElements: [],
                        graphicsPatterns: {}
                    };
                    
                    // Extract SVG elements
                    const svgs = document.querySelectorAll('svg');
                    svgs.forEach(svg => {
                        mediaInfo.svgElements.push({
                            viewBox: svg.getAttribute('viewBox'),
                            width: svg.getAttribute('width'),
                            height: svg.getAttribute('height'),
                            innerHTML: svg.innerHTML.substring(0, 500), // Limit size
                            className: svg.className.baseVal || svg.className
                        });
                    });
                    
                    // Extract background images
                    const allElements = document.querySelectorAll('*');
                    allElements.forEach(el => {
                        const styles = window.getComputedStyle(el);
                        if (styles.backgroundImage && styles.backgroundImage !== 'none') {
                            const rect = el.getBoundingClientRect();
                            if (rect.width > 100 && rect.height > 100) {
                                mediaInfo.backgroundImages.push({
                                    element: el.tagName,
                                    className: el.className,
                                    backgroundImage: styles.backgroundImage,
                                    backgroundSize: styles.backgroundSize,
                                    backgroundPosition: styles.backgroundPosition,
                                    dimensions: {
                                        width: rect.width,
                                        height: rect.height
                                    }
                                });
                            }
                        }
                    });
                    
                    // Extract icon patterns
                    const iconSelectors = [
                        '[class*="icon"]', '[class*="fa-"]', '[class*="material-"]',
                        'i[class]', '.icon', 'svg[class*="icon"]'
                    ];
                    
                    iconSelectors.forEach(selector => {
                        const icons = document.querySelectorAll(selector);
                        icons.forEach(icon => {
                            if (icon.offsetWidth < 50 && icon.offsetHeight < 50) {
                                mediaInfo.icons.push({
                                    className: icon.className,
                                    tag: icon.tagName,
                                    innerHTML: icon.innerHTML.substring(0, 200)
                                });
                            }
                        });
                    });
                    
                    // Extract canvas elements
                    const canvases = document.querySelectorAll('canvas');
                    canvases.forEach(canvas => {
                        mediaInfo.canvasElements.push({
                            width: canvas.width,
                            height: canvas.height,
                            className: canvas.className
                        });
                    });
                    
                    // Extract video elements
                    const videos = document.querySelectorAll('video');
                    videos.forEach(video => {
                        mediaInfo.videoElements.push({
                            src: video.src || video.currentSrc,
                            poster: video.poster,
                            autoplay: video.autoplay,
                            controls: video.controls,
                            loop: video.loop
                        });
                    });
                    
                    return mediaInfo;
                }
            ''')
            
            return media_data
        except Exception as e:
            logger.warning(f"Error extracting media: {e}")
            return {}

    async def _analyze_modern_design_trends(self) -> Dict[str, Any]:
        """Analyze modern design trends and patterns"""
        if not self.page:
            return {}
        
        try:
            trends_data = await self.page.evaluate('''
                () => {
                    const trends = {
                        designStyle: 'modern',
                        colorTrends: {},
                        typographyTrends: {},
                        layoutTrends: {},
                        interactionTrends: {},
                        aestheticScore: 0
                    };
                    
                    // Analyze color trends
                    const bodyStyles = window.getComputedStyle(document.body);
                    const bgColor = bodyStyles.backgroundColor;
                    const textColor = bodyStyles.color;
                    
                    // Determine if dark mode
                    const isDarkMode = bgColor.includes('rgb(') && 
                        bgColor.match(/rgb\\((\\d+),\\s*(\\d+),\\s*(\\d+)\\)/) &&
                        bgColor.match(/rgb\\((\\d+),\\s*(\\d+),\\s*(\\d+)\\)/)[1] < 50;
                    
                    trends.colorTrends = {
                        isDarkMode: isDarkMode,
                        primaryBackground: bgColor,
                        primaryText: textColor,
                        hasGradients: document.querySelector('[style*="gradient"]') !== null,
                        colorScheme: isDarkMode ? 'dark' : 'light'
                    };
                    
                    // Analyze typography trends
                    const headings = document.querySelectorAll('h1, h2, h3');
                    let totalFontWeight = 0;
                    let boldCount = 0;
                    
                    headings.forEach(h => {
                        const styles = window.getComputedStyle(h);
                        const weight = parseInt(styles.fontWeight) || 400;
                        totalFontWeight += weight;
                        if (weight >= 600) boldCount++;
                    });
                    
                    trends.typographyTrends = {
                        averageFontWeight: totalFontWeight / headings.length || 400,
                        usesBoldHeadings: boldCount > headings.length * 0.5,
                        primaryFont: bodyStyles.fontFamily,
                        hasCustomFonts: bodyStyles.fontFamily.includes('web') || 
                                       bodyStyles.fontFamily.includes('custom')
                    };
                    
                    // Analyze layout trends
                    const containers = document.querySelectorAll('div, section');
                    let flexCount = 0;
                    let gridCount = 0;
                    let hasCards = false;
                    
                    containers.forEach(container => {
                        const styles = window.getComputedStyle(container);
                        if (styles.display === 'flex') flexCount++;
                        if (styles.display === 'grid') gridCount++;
                        if (container.className.toLowerCase().includes('card') ||
                            (styles.borderRadius && styles.boxShadow)) {
                            hasCards = true;
                        }
                    });
                    
                    trends.layoutTrends = {
                        usesFlexbox: flexCount > 5,
                        usesGrid: gridCount > 2,
                        hasCardDesign: hasCards,
                        layoutComplexity: flexCount + gridCount,
                        isResponsive: document.querySelector('meta[name="viewport"]') !== null
                    };
                    
                    // Analyze interaction trends
                    const interactiveElements = document.querySelectorAll(
                        'button, a, [onclick], [data-toggle]'
                    );
                    let hasHoverEffects = false;
                    let hasAnimations = false;
                    
                    interactiveElements.forEach(el => {
                        const styles = window.getComputedStyle(el);
                        if (styles.transition && styles.transition !== 'none') {
                            hasHoverEffects = true;
                        }
                        if (styles.animation && styles.animation !== 'none') {
                            hasAnimations = true;
                        }
                    });
                    
                    trends.interactionTrends = {
                        hasHoverEffects: hasHoverEffects,
                        hasAnimations: hasAnimations,
                        hasModalElements: document.querySelector('.modal, .popup') !== null,
                        hasCarouselElements: document.querySelector('.carousel, .slider') !== null
                    };
                    
                    // Calculate aesthetic score
                    let score = 0;
                    if (trends.colorTrends.hasGradients) score += 10;
                    if (trends.layoutTrends.usesFlexbox) score += 15;
                    if (trends.layoutTrends.usesGrid) score += 15;
                    if (trends.layoutTrends.hasCardDesign) score += 10;
                    if (trends.interactionTrends.hasHoverEffects) score += 10;
                    if (trends.interactionTrends.hasAnimations) score += 20;
                    if (trends.typographyTrends.hasCustomFonts) score += 10;
                    if (trends.layoutTrends.isResponsive) score += 10;
                    
                    trends.aestheticScore = score;
                    
                    // Determine design style
                    if (score >= 70) trends.designStyle = 'cutting-edge';
                    else if (score >= 50) trends.designStyle = 'modern';
                    else if (score >= 30) trends.designStyle = 'contemporary';
                    else trends.designStyle = 'traditional';
                    
                    return trends;
                }
            ''')
            
            return trends_data
        except Exception as e:
            logger.warning(f"Error analyzing design trends: {e}")
            return {'designStyle': 'modern', 'aestheticScore': 50}

    def _generate_design_recommendations(self, visual_patterns: Dict, media_data: Dict, 
                                       design_trends: Dict) -> Dict[str, Any]:
        """Generate design recommendations based on analysis"""
        recommendations = {
            'color_scheme': 'modern-gradient',
            'layout_style': 'grid-based',
            'component_library': [],
            'visual_elements': [],
            'interaction_patterns': [],
            'graphics_suggestions': []
        }
        
        # Recommend color scheme based on trends
        if design_trends.get('colorTrends', {}).get('isDarkMode'):
            recommendations['color_scheme'] = 'dark-gradient'
        elif design_trends.get('aestheticScore', 0) > 60:
            recommendations['color_scheme'] = 'vibrant-modern'
        else:
            recommendations['color_scheme'] = 'clean-minimal'
        
        # Recommend layout based on patterns
        layout_patterns = visual_patterns.get('layouts', {}).get('patterns', {})
        if layout_patterns.get('grid', 0) > layout_patterns.get('flexbox', 0):
            recommendations['layout_style'] = 'css-grid-masonry'
        elif layout_patterns.get('cards', 0) > 3:
            recommendations['layout_style'] = 'card-grid-modern'
        else:
            recommendations['layout_style'] = 'flex-modern'
        
        # Recommend components based on found elements
        ui_components = visual_patterns.get('uiComponents', [])
        for component in ui_components:
            if component['count'] > 2:
                recommendations['component_library'].append(component['type'])
        
        # Add modern visual elements
        recommendations['visual_elements'] = [
            'gradient-backgrounds',
            'glassmorphism-cards',
            'floating-elements',
            'micro-animations',
            'modern-shadows',
            'rounded-corners',
            'icon-illustrations'
        ]
        
        # Add interaction patterns
        recommendations['interaction_patterns'] = [
            'hover-lift-effect',
            'smooth-transitions',
            'parallax-scrolling',
            'fade-in-animations',
            'button-ripple-effects'
        ]
        
        # Graphics suggestions based on media analysis
        if len(media_data.get('svgElements', [])) > 0:
            recommendations['graphics_suggestions'].append('custom-svg-icons')
        if len(media_data.get('backgroundImages', [])) > 0:
            recommendations['graphics_suggestions'].append('hero-backgrounds')
        
        recommendations['graphics_suggestions'].extend([
            'geometric-patterns',
            'abstract-shapes',
            'gradient-overlays',
            'modern-illustrations'
        ])
        
        return recommendations

    def _get_default_recommendations(self) -> Dict[str, Any]:
        """Get default design recommendations when analysis fails"""
        return {
            'color_scheme': 'modern-gradient',
            'layout_style': 'flex-modern',
            'component_library': ['button', 'card', 'nav'],
            'visual_elements': [
                'gradient-backgrounds',
                'glassmorphism-cards',
                'floating-elements',
                'micro-animations',
                'modern-shadows',
                'rounded-corners'
            ],
            'interaction_patterns': [
                'hover-lift-effect',
                'smooth-transitions',
                'fade-in-animations'
            ],
            'graphics_suggestions': [
                'geometric-patterns',
                'abstract-shapes',
                'gradient-overlays'
            ]
        }
    
    async def _handle_popups(self):
        """Handle common popups and cookie banners"""
        try:
            # Common cookie banner selectors
            popup_selectors = [
                '[id*="cookie"]', '[class*="cookie"]',
                '[id*="gdpr"]', '[class*="gdpr"]',
                '[id*="consent"]', '[class*="consent"]',
                '[id*="privacy"]', '[class*="privacy"]',
                '.modal', '.popup', '.overlay',
                '[role="dialog"]', '[role="alertdialog"]'
            ]
            
            for selector in popup_selectors:
                try:
                    # Check if popup exists
                    popup = await self.page.query_selector(selector)
                    if popup:
                        # Try to find and click accept/close buttons
                        close_buttons = await popup.query_selector_all(
                            'button:has-text("Accept"), button:has-text("Close"), button:has-text("OK"), '
                            'button:has-text("Agree"), button:has-text("Got it"), [aria-label="Close"], '
                            '.close, .dismiss, .accept'
                        )
                        
                        if close_buttons:
                            await close_buttons[0].click()
                            await self.page.wait_for_timeout(1000)
                            break
                except:
                    continue  # Try next selector
                    
        except Exception as e:
            logger.debug(f"Error handling popups: {e}")

    async def _capture_screenshots(self) -> Dict[str, str]:
        """Capture screenshots at different viewport sizes"""
        screenshots = {}
        
        try:
            viewport_sizes = [
                {'name': 'desktop', 'width': 1920, 'height': 1080},
                {'name': 'tablet', 'width': 768, 'height': 1024},
                {'name': 'mobile', 'width': 375, 'height': 667}
            ]
            
            for viewport in viewport_sizes:
                try:
                    await self.page.set_viewport_size({
                        'width': viewport['width'], 
                        'height': viewport['height']
                    })
                    await self.page.wait_for_timeout(1000)
                    
                    screenshot = await self.page.screenshot(full_page=True)
                    screenshots[viewport['name']] = base64.b64encode(screenshot).decode()
                    
                except Exception as e:
                    logger.warning(f"Failed to capture {viewport['name']} screenshot: {e}")
                    
        except Exception as e:
            logger.warning(f"Error capturing screenshots: {e}")
            
        return screenshots

    async def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get page performance metrics"""
        try:
            metrics = await self.page.evaluate('''
                () => {
                    const perfData = performance.getEntriesByType('navigation')[0];
                    const paintEntries = performance.getEntriesByType('paint');
                    
                    return {
                        loadTime: perfData ? perfData.loadEventEnd - perfData.loadEventStart : 0,
                        domContentLoaded: perfData ? perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart : 0,
                        firstPaint: paintEntries.find(p => p.name === 'first-paint')?.startTime || 0,
                        firstContentfulPaint: paintEntries.find(p => p.name === 'first-contentful-paint')?.startTime || 0,
                        transferSize: perfData ? perfData.transferSize : 0,
                        encodedBodySize: perfData ? perfData.encodedBodySize : 0,
                        decodedBodySize: perfData ? perfData.decodedBodySize : 0
                    };
                }
            ''')
            return metrics
        except Exception as e:
            logger.warning(f"Error getting performance metrics: {e}")
            return {}

    async def _extract_page_data(self, url: str, html_content: str) -> Dict[str, Any]:
        """Extract structured data from HTML content"""
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Basic page information
        data = {
            'url': url,
            'title': self._extract_title(soup),
            'meta_description': self._extract_meta_description(soup),
            'meta_keywords': self._extract_meta_keywords(soup),
            'canonical_url': self._extract_canonical_url(soup),
            'language': self._extract_language(soup),
            'html_content': html_content,
            'text_content': self._extract_text_content(soup),
            'word_count': len(self._extract_text_content(soup).split()),
            'structure': await self._analyze_structure(soup),
            'styles': await self._extract_styles(soup),
            'scripts': self._extract_scripts(soup),
            'images': await self._extract_images(soup, url),
            'links': self._extract_links(soup, url),
            'forms': self._extract_forms(soup),
            'navigation': self._extract_navigation(soup),
            'layout': await self._analyze_layout(),
            'colors': tuple(self._extract_colors(soup)),  # Convert to tuple
            'fonts': tuple(self._extract_fonts(soup)),    # Convert to tuple
            'responsive_breakpoints': await self._detect_responsive_design(),
            'social_media': self._extract_social_media(soup),
            'structured_data': tuple(self._extract_structured_data(soup)),  # Convert to tuple
            'favicon': self._extract_favicon(soup, url),
            'analytics': self._extract_analytics(soup)
        }
        
        return data

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title"""
        title_tag = soup.find('title')
        return title_tag.get_text().strip() if title_tag else "Untitled"

    def _extract_meta_description(self, soup: BeautifulSoup) -> str:
        """Extract meta description"""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if not meta_desc:
            meta_desc = soup.find('meta', attrs={'property': 'og:description'})
        return meta_desc.get('content', '').strip() if meta_desc else ""

    def _extract_meta_keywords(self, soup: BeautifulSoup) -> str:
        """Extract meta keywords"""
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        return meta_keywords.get('content', '').strip() if meta_keywords else ""

    def _extract_canonical_url(self, soup: BeautifulSoup) -> str:
        """Extract canonical URL"""
        canonical = soup.find('link', attrs={'rel': 'canonical'})
        return canonical.get('href', '').strip() if canonical else ""

    def _extract_language(self, soup: BeautifulSoup) -> str:
        """Extract page language"""
        html_tag = soup.find('html')
        if html_tag and html_tag.get('lang'):
            return html_tag.get('lang')
        
        meta_lang = soup.find('meta', attrs={'http-equiv': 'content-language'})
        if meta_lang:
            return meta_lang.get('content', '')
        
        return "en"  # Default to English

    def _extract_text_content(self, soup: BeautifulSoup) -> str:
        """Extract clean text content"""
        # Remove script and style elements
        for script in soup(["script", "style", "noscript"]):
            script.decompose()
        
        # Get text and clean it
        text = soup.get_text(separator=' ', strip=True)
        
        # Clean up extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()

    async def _analyze_structure(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze the HTML structure"""
        structure = {
            'headings': (),  # Will be converted to tuple
            'sections': (),  # Will be converted to tuple
            'semantic_elements': (),  # Will be converted to tuple
            'hierarchy': {},
            'content_blocks': ()  # Will be converted to tuple
        }
        
        headings = []
        # Extract headings with hierarchy
        for i in range(1, 7):
            heading_tags = soup.find_all(f'h{i}')
            for h in heading_tags:
                headings.append({
                    'level': i,
                    'text': h.get_text().strip(),
                    'id': h.get('id'),
                    'class': tuple(h.get('class', [])),  # Convert to tuple
                    'position': len(headings)
                })
        structure['headings'] = tuple(headings)  # Convert to tuple
        
        semantic_elements = []
        # Extract semantic elements
        semantic_tags = ('header', 'nav', 'main', 'section', 'article', 'aside', 'footer')
        for tag in semantic_tags:
            elements = soup.find_all(tag)
            for el in elements:
                semantic_elements.append({
                    'tag': tag,
                    'id': el.get('id'),
                    'class': tuple(el.get('class', [])),  # Convert to tuple
                    'text_preview': el.get_text()[:100].strip(),
                    'children_count': len(el.find_all())
                })
        structure['semantic_elements'] = tuple(semantic_elements)  # Convert to tuple
        
        content_blocks = []
        # Extract major content blocks
        content_containers = soup.find_all(('div', 'section', 'article'), class_=True)
        for container in content_containers[:20]:  # Limit to first 20
            class_names = ' '.join(container.get('class', []))
            if any(keyword in class_names.lower() for keyword in ('content', 'main', 'body', 'article', 'post')):
                content_blocks.append({
                    'tag': container.name,
                    'classes': class_names,
                    'id': container.get('id', ''),
                    'text_length': len(container.get_text().strip()),
                    'child_count': len(container.find_all())
                })
        structure['content_blocks'] = tuple(content_blocks)  # Convert to tuple
        
        return structure

    async def _extract_styles(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract CSS styles"""
        styles = {
            'inline_styles': (),  # Will be converted to tuple
            'style_sheets': (),   # Will be converted to tuple
            'external_css': (),   # Will be converted to tuple
            'css_variables': (),  # Will be converted to tuple
            'media_queries': ()   # Will be converted to tuple
        }
        
        # Extract inline styles
        elements_with_style = soup.find_all(style=True)
        inline_styles = tuple(el.get('style') for el in elements_with_style[:20])  # Limit to first 20
        styles['inline_styles'] = inline_styles
        
        style_sheets = []
        css_variables = []
        media_queries = []
        
        # Extract internal CSS
        style_tags = soup.find_all('style')
        for style in style_tags:
            css_content = style.get_text()
            style_sheets.append(css_content)
            
            # Extract CSS variables
            css_vars = re.findall(r'--[\w-]+:\s*[^;]+', css_content)
            css_variables.extend(css_vars)
            
            # Extract media queries
            media_q = re.findall(r'@media[^{]+{[^}]*}', css_content, re.DOTALL)
            media_queries.extend(media_q)
        
        styles['style_sheets'] = tuple(style_sheets)
        styles['css_variables'] = tuple(css_variables)
        styles['media_queries'] = tuple(media_queries)
        
        # Extract external CSS links
        css_links = soup.find_all('link', rel='stylesheet')
        external_css = tuple(link.get('href') for link in css_links if link.get('href'))
        styles['external_css'] = external_css
        
        return styles

    def _extract_scripts(self, soup: BeautifulSoup) -> Dict[str, Tuple]:
        """Extract JavaScript references and inline scripts"""
        scripts = {
            'external': (),
            'inline': (),
            'frameworks_detected': ()
        }
        
        external = []
        inline = []
        frameworks_detected = []
        
        script_tags = soup.find_all('script')
        
        for script in script_tags:
            if script.get('src'):
                src = script.get('src')
                external.append(src)
                
                # Detect common frameworks
                if any(framework in src.lower() for framework in ('react', 'vue', 'angular', 'jquery')):
                    framework_name = next(fw for fw in ('react', 'vue', 'angular', 'jquery') if fw in src.lower())
                    if framework_name not in frameworks_detected:
                        frameworks_detected.append(framework_name)
                        
            elif script.string:
                # Include inline scripts (first 200 chars)
                inline_content = script.string[:200].strip()
                if inline_content:
                    inline.append(inline_content)
        
        scripts['external'] = tuple(external)
        scripts['inline'] = tuple(inline)
        scripts['frameworks_detected'] = tuple(frameworks_detected)
        
        return scripts

    async def _extract_images(self, soup: BeautifulSoup, base_url: str) -> Tuple[Dict[str, Any], ...]:
        """Extract image information"""
        images = []
        img_tags = soup.find_all('img')
        
        for img in img_tags[:30]:  # Limit to first 30 images
            src = img.get('src', '')
            if src:
                # Make absolute URL
                if src.startswith('//'):
                    src = 'https:' + src
                elif src.startswith('/'):
                    src = urljoin(base_url, src)
                elif not src.startswith(('http://', 'https://')):
                    src = urljoin(base_url, src)
            
            images.append({
                'src': src,
                'alt': img.get('alt', ''),
                'title': img.get('title', ''),
                'width': img.get('width', ''),
                'height': img.get('height', ''),
                'class': ' '.join(img.get('class', [])),
                'loading': img.get('loading', ''),
                'srcset': img.get('srcset', ''),
                'sizes': img.get('sizes', ''),
                'data_src': img.get('data-src', ''),  # Lazy loading
                'is_decorative': not img.get('alt', '').strip()
            })
        
        return tuple(images)  # Convert to tuple

    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> Dict[str, Tuple]:
        """Extract link information categorized by type"""
        links = {
            'internal': (),
            'external': (),
            'email': (),
            'phone': (),
            'download': ()
        }
        
        internal = []
        external = []
        email = []
        phone = []
        download = []
        
        a_tags = soup.find_all('a', href=True)
        base_domain = urlparse(base_url).netloc
        
        for link in a_tags[:100]:  # Limit to first 100 links
            href = link.get('href', '').strip()
            text = link.get_text().strip()
            
            if not href:
                continue
            
            link_data = {
                'href': href,
                'text': text,
                'title': link.get('title', ''),
                'target': link.get('target', ''),
                'class': ' '.join(link.get('class', [])),
                'rel': ' '.join(link.get('rel', []))
            }
            
            # Categorize links
            if href.startswith('mailto:'):
                email.append(link_data)
            elif href.startswith('tel:'):
                phone.append(link_data)
            elif any(ext in href.lower() for ext in ('.pdf', '.doc', '.zip', '.mp3', '.mp4')):
                download.append(link_data)
            elif href.startswith(('http://', 'https://')):
                if base_domain in href:
                    internal.append(link_data)
                else:
                    external.append(link_data)
            else:
                internal.append(link_data)
        
        links['internal'] = tuple(internal)
        links['external'] = tuple(external)
        links['email'] = tuple(email)
        links['phone'] = tuple(phone)
        links['download'] = tuple(download)
        
        return links

    def _extract_forms(self, soup: BeautifulSoup) -> Tuple[Dict[str, Any], ...]:
        """Extract form information"""
        forms = []
        form_tags = soup.find_all('form')
        
        for form in form_tags:
            fields = []
            buttons = []
            
            form_data = {
                'action': form.get('action', ''),
                'method': form.get('method', 'get').lower(),
                'enctype': form.get('enctype', ''),
                'id': form.get('id', ''),
                'class': ' '.join(form.get('class', [])),
                'fields': (),  # Will be converted to tuple
                'buttons': ()  # Will be converted to tuple
            }
            
            # Extract form fields
            inputs = form.find_all(('input', 'textarea', 'select'))
            for input_field in inputs:
                field_data = {
                    'tag': input_field.name,
                    'type': input_field.get('type', ''),
                    'name': input_field.get('name', ''),
                    'id': input_field.get('id', ''),
                    'placeholder': input_field.get('placeholder', ''),
                    'required': input_field.has_attr('required'),
                    'class': ' '.join(input_field.get('class', [])),
                    'value': input_field.get('value', '')
                }
                
                # Special handling for select elements
                if input_field.name == 'select':
                    options = input_field.find_all('option')
                    field_data['options'] = tuple(
                        {'value': opt.get('value', ''), 'text': opt.get_text().strip()}
                        for opt in options
                    )
                
                fields.append(field_data)
            
            # Extract buttons
            button_tags = form.find_all(('button', 'input[type="submit"]', 'input[type="button"]'))
            for button in button_tags:
                button_data = {
                    'tag': button.name,
                    'type': button.get('type', ''),
                    'text': button.get_text().strip() or button.get('value', ''),
                    'class': ' '.join(button.get('class', []))
                }
                buttons.append(button_data)
            
            form_data['fields'] = tuple(fields)
            form_data['buttons'] = tuple(buttons)
            forms.append(form_data)
        
        return tuple(forms)

    def _extract_navigation(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract navigation structure"""
        nav_data = {
            'nav_elements': (),
            'breadcrumbs': (),
            'menu_structure': ()
        }
        
        nav_elements = []
        breadcrumbs = []
        
        # Find navigation elements
        nav_tags = soup.find_all('nav')
        for nav in nav_tags:
            links = []
            
            nav_info = {
                'class': ' '.join(nav.get('class', [])),
                'id': nav.get('id', ''),
                'role': nav.get('role', ''),
                'links': (),  # Will be converted to tuple
                'sublists': ()  # Will be converted to tuple
            }
            
            # Extract links within nav
            nav_links = nav.find_all('a')
            for link in nav_links:
                links.append({
                    'href': link.get('href', ''),
                    'text': link.get_text().strip(),
                    'class': ' '.join(link.get('class', []))
                })
            
            # Extract nested lists (dropdowns/submenus)
            sublists = nav.find_all('ul')
            
            nav_info['links'] = tuple(links)
            nav_info['sublists'] = len(sublists)
            nav_elements.append(nav_info)
        
        nav_data['nav_elements'] = tuple(nav_elements)
        
        # Look for breadcrumbs
        breadcrumb_selectors = [
            '[class*="breadcrumb"]',
            '[id*="breadcrumb"]',
            'nav ol',
            '.breadcrumbs'
        ]
        
        for selector in breadcrumb_selectors:
            breadcrumb_tags = soup.select(selector)
            for bc in breadcrumb_tags:
                links = bc.find_all('a')
                if links:
                    breadcrumbs.append(tuple(
                        {'text': link.get_text().strip(), 'href': link.get('href', '')}
                        for link in links
                    ))
        
        nav_data['breadcrumbs'] = tuple(breadcrumbs)
        
        return nav_data

    async def _analyze_layout(self) -> Dict[str, Any]:
        """Analyze the page layout using Playwright"""
        if not self.page:
            return {}
        
        try:
            # Get layout information
            layout_info = await self.page.evaluate('''
                () => {
                    const containers = document.querySelectorAll('div, section, main, header, footer, article, aside');
                    const layout = [];
                    
                    for (let i = 0; i < Math.min(containers.length, 30); i++) {
                        const container = containers[i];
                        const rect = container.getBoundingClientRect();
                        const styles = window.getComputedStyle(container);
                        
                        // Only include visible elements
                        if (rect.width > 0 && rect.height > 0) {
                            layout.push({
                                tagName: container.tagName,
                                className: container.className,
                                id: container.id,
                                position: {
                                    x: Math.round(rect.x),
                                    y: Math.round(rect.y),
                                    width: Math.round(rect.width),
                                    height: Math.round(rect.height)
                                },
                                styles: {
                                    display: styles.display,
                                    position: styles.position,
                                    zIndex: styles.zIndex,
                                    flexDirection: styles.flexDirection,
                                    gridTemplateColumns: styles.gridTemplateColumns,
                                    backgroundColor: styles.backgroundColor,
                                    padding: styles.padding,
                                    margin: styles.margin
                                }
                            });
                        }
                    }
                    
                    return {
                        viewport: { 
                            width: window.innerWidth, 
                            height: window.innerHeight 
                        },
                        containers: layout,
                        bodyStyles: {
                            fontFamily: window.getComputedStyle(document.body).fontFamily,
                            fontSize: window.getComputedStyle(document.body).fontSize,
                            backgroundColor: window.getComputedStyle(document.body).backgroundColor,
                            color: window.getComputedStyle(document.body).color
                        }
                    };
                }
            ''')
            
            # Convert containers to tuple for hashability
            if 'containers' in layout_info:
                layout_info['containers'] = tuple(layout_info['containers'])
            
            return layout_info
        except Exception as e:
            logger.warning(f"Error analyzing layout: {e}")
            return {}

    def _extract_colors(self, soup: BeautifulSoup) -> Tuple[str, ...]:
        """Extract color palette from styles"""
        colors = set()
        
        # Extract from inline styles
        elements_with_style = soup.find_all(style=True)
        for el in elements_with_style:
            style = el.get('style', '')
            # Extract hex colors
            hex_colors = re.findall(r'#[0-9a-fA-F]{3,6}', style)
            colors.update(hex_colors)
            # Extract rgb colors
            rgb_colors = re.findall(r'rgb\([^)]+\)', style)
            colors.update(rgb_colors)
        
        # Extract from CSS
        style_tags = soup.find_all('style')
        for style in style_tags:
            css_content = style.get_text()
            hex_colors = re.findall(r'#[0-9a-fA-F]{3,6}', css_content)
            colors.update(hex_colors)
            rgb_colors = re.findall(r'rgb\([^)]+\)', css_content)
            colors.update(rgb_colors)
        
        return tuple(list(colors)[:30])  # Limit to 30 colors and convert to tuple

    def _extract_fonts(self, soup: BeautifulSoup) -> Tuple[str, ...]:
        """Extract font families used"""
        fonts = set()
        
        # Extract from inline styles
        elements_with_style = soup.find_all(style=True)
        for el in elements_with_style:
            style = el.get('style', '')
            if 'font-family' in style:
                font_match = re.search(r'font-family:\s*([^;]+)', style, re.IGNORECASE)
                if font_match:
                    font_family = font_match.group(1).strip().replace('"', "'")
                    fonts.add(font_family)
        
        # Extract from CSS
        style_tags = soup.find_all('style')
        for style in style_tags:
            css_content = style.get_text()
            font_matches = re.findall(r'font-family:\s*([^;]+)', css_content, re.IGNORECASE)
            for font_match in font_matches:
                font_family = font_match.strip().replace('"', "'")
                fonts.add(font_family)
        
        return tuple(list(fonts)[:15])  # Limit to 15 fonts and convert to tuple

    async def _detect_responsive_design(self) -> Dict[str, Any]:
        """Detect responsive design patterns"""
        if not self.page:
            return {}
        
        try:
            # Check for viewport meta tag
            viewport_meta = await self.page.evaluate('''
                () => {
                    const meta = document.querySelector('meta[name="viewport"]');
                    return meta ? meta.getAttribute('content') : null;
                }
            ''')
            
            # Test different viewport sizes
            breakpoints = []
            test_widths = [320, 768, 1024, 1440]
            
            for width in test_widths:
                try:
                    await self.page.set_viewport_size({"width": width, "height": 800})
                    await self.page.wait_for_timeout(500)
                    
                    # Check if layout changes
                    layout_info = await self.page.evaluate(f'''
                        () => {{
                            const body = document.body;
                            const computedStyle = window.getComputedStyle(body);
                            const container = document.querySelector('main, .container, .wrapper, .content') || body;
                            const containerStyle = window.getComputedStyle(container);
                            
                            return {{
                                width: {width},
                                bodyWidth: body.offsetWidth,
                                fontSize: computedStyle.fontSize,
                                containerMaxWidth: containerStyle.maxWidth,
                                containerPadding: containerStyle.padding,
                                gridColumns: containerStyle.gridTemplateColumns,
                                flexDirection: containerStyle.flexDirection
                            }};
                        }}
                    ''')
                    
                    breakpoints.append(layout_info)
                except Exception as e:
                    logger.warning(f"Error testing viewport {width}: {e}")
            
            return {
                'viewport_meta': viewport_meta,
                'breakpoint_tests': tuple(breakpoints),  # Convert to tuple
                'is_responsive': viewport_meta is not None and 'width=device-width' in (viewport_meta or ''),
                'has_media_queries': len(breakpoints) > 1 and any(
                    bp['containerMaxWidth'] != breakpoints[0]['containerMaxWidth'] 
                    for bp in breakpoints[1:]
                )
            }
        except Exception as e:
            logger.warning(f"Error detecting responsive design: {e}")
            return {'is_responsive': False}

    def _extract_social_media(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract social media information"""
        social_data = {
            'og_tags': {},
            'twitter_cards': {},
            'social_links': ()  # Will be converted to tuple
        }
        
        # Extract Open Graph tags
        og_tags = soup.find_all('meta', property=lambda x: x and x.startswith('og:'))
        for tag in og_tags:
            property_name = tag.get('property', '').replace('og:', '')
            content = tag.get('content', '')
            if property_name and content:
                social_data['og_tags'][property_name] = content
        
        # Extract Twitter Card tags
        twitter_tags = soup.find_all('meta', attrs={'name': lambda x: x and x.startswith('twitter:')})
        for tag in twitter_tags:
            name = tag.get('name', '').replace('twitter:', '')
            content = tag.get('content', '')
            if name and content:
                social_data['twitter_cards'][name] = content
        
        # Extract social media links
        social_platforms = ('facebook', 'twitter', 'instagram', 'linkedin', 'youtube', 'tiktok', 'pinterest')
        social_links = soup.find_all('a', href=True)
        
        links = []
        for link in social_links:
            href = link.get('href', '').lower()
            for platform in social_platforms:
                if platform in href:
                    links.append({
                        'platform': platform,
                        'url': link.get('href'),
                        'text': link.get_text().strip(),
                        'class': ' '.join(link.get('class', []))
                    })
                    break
        
        social_data['social_links'] = tuple(links)  # Convert to tuple
        
        return social_data

    def _extract_structured_data(self, soup: BeautifulSoup) -> Tuple[Dict[str, Any], ...]:
        """Extract structured data (JSON-LD, microdata)"""
        structured_data = []
        
        # Extract JSON-LD
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_ld_scripts:
            try:
                data = json.loads(script.string)
                structured_data.append({
                    'type': 'json-ld',
                    'data': data
                })
            except (json.JSONDecodeError, TypeError):
                continue
        
        # Extract microdata
        microdata_elements = soup.find_all(attrs={'itemscope': True})
        for element in microdata_elements[:10]:  # Limit to first 10
            item_data = {
                'type': 'microdata',
                'itemtype': element.get('itemtype', ''),
                'properties': {}
            }
            
            # Find properties within this scope
            props = element.find_all(attrs={'itemprop': True})
            for prop in props:
                prop_name = prop.get('itemprop')
                prop_value = prop.get('content') or prop.get_text().strip()
                item_data['properties'][prop_name] = prop_value
            
            if item_data['properties']:
                structured_data.append(item_data)
        
        return tuple(structured_data)  # Convert to tuple

    def _extract_favicon(self, soup: BeautifulSoup, base_url: str) -> Dict[str, Dict[str, str]]:
        """Extract favicon information"""
        favicon_data = {}
        
        # Common favicon selectors
        favicon_selectors = [
            'link[rel="icon"]',
            'link[rel="shortcut icon"]',
            'link[rel="apple-touch-icon"]',
            'link[rel="apple-touch-icon-precomposed"]'
        ]
        
        for selector in favicon_selectors:
            favicon = soup.select_one(selector)
            if favicon and favicon.get('href'):
                href = favicon.get('href')
                
                # Make absolute URL
                if href.startswith('//'):
                    href = 'https:' + href
                elif href.startswith('/'):
                    href = urljoin(base_url, href)
                elif not href.startswith(('http://', 'https://')):
                    href = urljoin(base_url, href)
                
                rel = favicon.get('rel', 'icon')
                favicon_data[rel] = {
                    'href': href,
                    'sizes': favicon.get('sizes', ''),
                    'type': favicon.get('type', '')
                }
        
        # Default favicon location
        if not favicon_data:
            favicon_data['icon'] = {
                'href': urljoin(base_url, '/favicon.ico'),
                'sizes': '',
                'type': 'image/x-icon'
            }
        
        return favicon_data

    def _extract_analytics(self, soup: BeautifulSoup) -> Dict[str, Tuple[str, ...]]:
        """Extract analytics and tracking information"""
        analytics = {
            'google_analytics': (),
            'google_tag_manager': (),
            'facebook_pixel': (),
            'other_tracking': ()
        }
        
        google_analytics = []
        google_tag_manager = []
        facebook_pixel = []
        other_tracking = []
        
        # Look in script tags for tracking codes
        scripts = soup.find_all('script')
        for script in scripts:
            script_content = script.get_text().lower()
            src = script.get('src', '').lower()
            
            # Google Analytics
            if 'google-analytics.com' in src or 'gtag(' in script_content or 'ga(' in script_content:
                # Extract GA tracking ID
                ga_matches = re.findall(r'["\']UA-\d+-\d+["\']', script_content)
                ga_matches.extend(re.findall(r'["\']G-[A-Z0-9]+["\']', script_content))
                google_analytics.extend([match.strip('"\'') for match in ga_matches])
            
            # Google Tag Manager
            if 'googletagmanager.com' in src or 'gtm-' in script_content:
                gtm_matches = re.findall(r'["\']GTM-[A-Z0-9]+["\']', script_content)
                google_tag_manager.extend([match.strip('"\'') for match in gtm_matches])
            
            # Facebook Pixel
            if 'connect.facebook.net' in src or 'fbq(' in script_content:
                fb_matches = re.findall(r'fbq\(["\']init["\'],\s*["\'](\d+)["\']', script_content)
                facebook_pixel.extend(fb_matches)
            
            # Other tracking services
            tracking_domains = ('hotjar', 'mixpanel', 'segment', 'amplitude', 'intercom')
            for domain in tracking_domains:
                if domain in src or domain in script_content:
                    other_tracking.append(domain)
        
        # Remove duplicates and convert to tuples
        analytics['google_analytics'] = tuple(set(google_analytics))
        analytics['google_tag_manager'] = tuple(set(google_tag_manager))
        analytics['facebook_pixel'] = tuple(set(facebook_pixel))
        analytics['other_tracking'] = tuple(set(other_tracking))
        
        return analytics

    async def scrape_multiple_pages(self, urls: Tuple[str, ...], max_concurrent: int = 3) -> Dict[str, Dict[str, Any]]:
        """Scrape multiple pages concurrently"""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def scrape_single(url: str) -> Tuple[str, Dict[str, Any]]:
            async with semaphore:
                try:
                    result = await self.scrape_website(url)
                    return url, result
                except Exception as e:
                    logger.error(f"Failed to scrape {url}: {e}")
                    return url, {'error': str(e)}
        
        # Execute scraping tasks concurrently
        tasks = [scrape_single(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Organize results
        scraped_data = {}
        for result in results:
            if isinstance(result, tuple):
                url, data = result
                scraped_data[url] = data
            else:
                logger.error(f"Unexpected result type: {type(result)}")
        
        return scraped_data

    async def get_page_insights(self, url: str) -> Dict[str, Any]:
        """Get additional page insights using Playwright"""
        if not self.page:
            raise Exception("Page not initialized. Call scrape_website first.")
        
        try:
            insights = await self.page.evaluate('''
                () => {
                    const insights = {};
                    
                    // Count elements
                    insights.elementCounts = {
                        total: document.querySelectorAll('*').length,
                        divs: document.querySelectorAll('div').length,
                        images: document.querySelectorAll('img').length,
                        links: document.querySelectorAll('a').length,
                        forms: document.querySelectorAll('form').length,
                        inputs: document.querySelectorAll('input').length,
                        buttons: document.querySelectorAll('button').length
                    };
                    
                    // Check for common libraries/frameworks
                    insights.librariesDetected = [];
                    if (window.jQuery) insights.librariesDetected.push('jQuery');
                    if (window.React) insights.librariesDetected.push('React');
                    if (window.Vue) insights.librariesDetected.push('Vue');
                    if (window.angular) insights.librariesDetected.push('Angular');
                    if (window.bootstrap) insights.librariesDetected.push('Bootstrap');
                    
                    // Page load state
                    insights.loadState = {
                        readyState: document.readyState,
                        hidden: document.hidden,
                        visibilityState: document.visibilityState
                    };
                    
                    // Viewport and scroll info
                    insights.viewport = {
                        width: window.innerWidth,
                        height: window.innerHeight,
                        scrollHeight: document.documentElement.scrollHeight,
                        scrollTop: window.pageYOffset || document.documentElement.scrollTop
                    };
                    
                    return insights;
                }
            ''')
            
            # Convert librariesDetected to tuple for hashability
            if 'librariesDetected' in insights:
                insights['librariesDetected'] = tuple(insights['librariesDetected'])
            
            return insights
            
        except Exception as e:
            logger.warning(f"Error getting page insights: {e}")
            return {}

    def get_scraping_summary(self, scraped_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of the scraped data"""
        summary = {
            'url': scraped_data.get('url', ''),
            'title': scraped_data.get('title', ''),
            'word_count': scraped_data.get('word_count', 0),
            'image_count': len(scraped_data.get('images', ())),
            'link_count': sum(len(links) for links in scraped_data.get('links', {}).values()),
            'form_count': len(scraped_data.get('forms', ())),
            'heading_count': len(scraped_data.get('structure', {}).get('headings', ())),
            'color_count': len(scraped_data.get('colors', ())),
            'font_count': len(scraped_data.get('fonts', ())),
            'has_responsive_design': scraped_data.get('responsive_breakpoints', {}).get('is_responsive', False),
            'has_social_media': bool(scraped_data.get('social_media', {}).get('social_links', ())),
            'has_analytics': any(scraped_data.get('analytics', {}).values()),
            'performance_score': self._calculate_performance_score(scraped_data),
            'complexity_score': self._calculate_complexity_score(scraped_data),
            'design_style': scraped_data.get('design_trends', {}).get('designStyle', 'modern'),
            'aesthetic_score': scraped_data.get('design_trends', {}).get('aestheticScore', 50)
        }
        
        return summary

    def _calculate_performance_score(self, scraped_data: Dict[str, Any]) -> float:
        """Calculate a simple performance score (0-100)"""
        score = 100.0
        
        # Deduct points for large numbers of elements
        image_count = len(scraped_data.get('images', ()))
        if image_count > 50:
            score -= min(20, (image_count - 50) * 0.5)
        
        # Deduct points for external scripts
        external_scripts = len(scraped_data.get('scripts', {}).get('external', ()))
        if external_scripts > 10:
            score -= min(15, (external_scripts - 10) * 1.5)
        
        # Deduct points for large CSS files
        css_count = len(scraped_data.get('styles', {}).get('external_css', ()))
        if css_count > 5:
            score -= min(10, (css_count - 5) * 2)
        
        return max(0, score)

    def _calculate_complexity_score(self, scraped_data: Dict[str, Any]) -> float:
        """Calculate a website complexity score (0-100)"""
        score = 0
        
        # Add points for various elements
        score += min(20, len(scraped_data.get('structure', {}).get('headings', ())) * 2)
        score += min(15, len(scraped_data.get('forms', ())) * 5)
        score += min(10, len(scraped_data.get('images', ())) * 0.2)
        score += min(15, len(scraped_data.get('scripts', {}).get('external', ())) * 1.5)
        score += min(10, len(scraped_data.get('styles', {}).get('external_css', ())) * 2)
        
        # Add points for advanced features
        if scraped_data.get('responsive_breakpoints', {}).get('is_responsive'):
            score += 10
        if scraped_data.get('social_media', {}).get('social_links'):
            score += 5
        if any(scraped_data.get('analytics', {}).values()):
            score += 5
        if scraped_data.get('structured_data'):
            score += 10
        
        return min(100, score)