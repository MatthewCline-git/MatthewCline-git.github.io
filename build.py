import os
import shutil
from datetime import datetime
from pathlib import Path
import markdown
import frontmatter
from jinja2 import Environment, FileSystemLoader
from feedgen.feed import FeedGenerator

# Site Configuration
CONFIG = {
    'base_url': '/docs',  # Empty for root, '/repo-name' for project page
    'site_name': 'Matthew Cline',
    'site_description': 'writing, coding, teaching',
    'site_url': 'https://your-username.github.io',  # Update this
    'author': 'Matthew Cline'
}

# Set up Jinja2 environment
env = Environment(loader=FileSystemLoader('templates'))

def ensure_directory(path: Path):
    """Create directory if it doesn't exist"""
    path.mkdir(parents=True, exist_ok=True)

def create_docs_dir():
    """Create docs directory if it doesn't exist, clear if it does"""
    try:
        docs_path = Path('docs')
        if docs_path.exists():
            shutil.rmtree(docs_path)
        docs_path.mkdir()
        (docs_path / 'essays').mkdir()
    except PermissionError:
        print("Error: Permission denied when creating docs directory")
        raise
    except Exception as e:
        print(f"Error creating docs directory: {e}")
        raise

def copy_static_files():
    """Copy static files to docs directory"""
    static_path = Path('static')
    if static_path.exists():
        try:
            dest_path = Path('docs/static')
            if dest_path.exists():
                shutil.rmtree(dest_path)
            shutil.copytree(static_path, dest_path)
        except Exception as e:
            print(f"Error copying static files: {e}")
            raise

def read_essay_file(filepath: Path):
    """Read and parse a markdown essay file with frontmatter"""
    try:
        with open(filepath) as f:
            post = frontmatter.load(f)
        
        # Convert markdown to HTML with extensions
        md = markdown.Markdown(extensions=[
            'markdown.extensions.fenced_code',  # For code blocks with ```
            'markdown.extensions.tables',       # For tables
            'markdown.extensions.footnotes',    # For footnotes
            'markdown.extensions.toc',          # For table of contents
            'markdown.extensions.attr_list',    # For adding classes to elements
            'markdown.extensions.meta'          # For metadata in markdown
        ])
        
        content = md.convert(post.content)
        
        # Extract preview (first paragraph)
        # Remove HTML tags for cleaner preview
        preview = content.split('</p>')[0]
        preview = preview.replace('<p>', '')
        if len(preview) > 200:
            preview = preview[:200] + '...'
        
        # Get metadata from frontmatter or use defaults
        metadata = {
            'title': post.get('title', 'Untitled'),
            'date': post.get('date', datetime.now().strftime('%B %d, %Y')),
            'preview': preview,
            'content': content,
            'slug': filepath.stem,  # Using pathlib's stem property
            'tags': post.get('tags', []),
            'author': post.get('author', CONFIG['author'])
        }
        
        return metadata
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        raise

def generate_rss_feed(essays):
    """Generate RSS feed from essays"""
    try:
        fg = FeedGenerator()
        fg.title(CONFIG['site_name'])
        fg.description(CONFIG['site_description'])
        fg.link(href=CONFIG['site_url'])
        fg.language('en')

        for essay in essays:
            fe = fg.add_entry()
            fe.title(essay['title'])
            fe.description(essay['preview'])
            fe.link(href=f"{CONFIG['site_url']}/essays/{essay['slug']}.html")
            # Convert date string to datetime object
            essay_date = datetime.strptime(essay['date'], '%B %d, %Y')
            fe.published(essay_date)
            fe.author(name=essay['author'])

        fg.rss_file('docs/feed.xml')
    except Exception as e:
        print(f"Error generating RSS feed: {e}")
        # Don't raise here - RSS feed is optional

def build_site():
    """Build the entire site"""
    try:
        # Ensure required directories exist
        content_path = Path('content/essays')
        if not content_path.exists():
            print(f"Warning: Content directory {content_path} does not exist")
            ensure_directory(content_path)

        # Create fresh docs directory
        create_docs_dir()
        copy_static_files()
        
        # Read all essays
        essays = []
        for essay_file in content_path.glob('*.md'):
            try:
                essay_data = read_essay_file(essay_file)
                essays.append(essay_data)
            except Exception as e:
                print(f"Error processing {essay_file}: {e}")
                continue
        
        # Sort essays by date (newest first)
        essays.sort(key=lambda x: datetime.strptime(x['date'], '%B %d, %Y'), reverse=True)
        
        # Generate index page with recent essays
        index_template = env.get_template('index.html')
        output = index_template.render(recent_essays=essays[:3], config=CONFIG)
        with open('docs/index.html', 'w', encoding='utf-8') as f:
            f.write(output)
        
        # Generate writing index page
        writing_template = env.get_template('writing.html')
        output = writing_template.render(essays=essays, config=CONFIG)
        with open('docs/writing.html', 'w', encoding='utf-8') as f:
            f.write(output)
        
        # Generate individual essay pages
        essay_template = env.get_template('essay.html')
        for essay in essays:
            output = essay_template.render(essay=essay, config=CONFIG)
            essay_path = Path('docs/essays') / f"{essay['slug']}.html"
            with open(essay_path, 'w', encoding='utf-8') as f:
                f.write(output)
        
        # Generate RSS feed
        generate_rss_feed(essays)
        
        print(f"Built {len(essays)} essays")
        print("Site built successfully!")

    except Exception as e:
        print(f"Error building site: {e}")
        raise

if __name__ == '__main__':
    build_site()