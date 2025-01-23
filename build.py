import os
import shutil
from datetime import datetime
from pathlib import Path
import markdown
import frontmatter
from jinja2 import Environment, FileSystemLoader

# Set up Jinja2 environment
env = Environment(loader=FileSystemLoader('templates'))

def create_docs_dir():
    """Create docs directory if it doesn't exist, clear if it does"""
    if os.path.exists('docs'):
        shutil.rmtree('docs')
    os.makedirs('docs')
    os.makedirs('docs/essays')

def copy_static_files():
    """Copy static files to docs directory"""
    if os.path.exists('static'):
        shutil.copytree('static', 'docs/static')

def read_essay_file(filepath):
    """Read and parse a markdown essay file with frontmatter"""
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
        'slug': os.path.splitext(os.path.basename(filepath))[0],
        'tags': post.get('tags', []),
        'author': post.get('author', 'Matthew Cline')
    }
    
    return metadata

def build_site():
    """Build the entire site"""
    # Create fresh docs directory
    create_docs_dir()
    copy_static_files()
    
    # Read all essays
    essays = []
    essays_dir = Path('content/essays')
    if essays_dir.exists():
        for essay_file in essays_dir.glob('*.md'):
            try:
                essay_data = read_essay_file(essay_file)
                essays.append(essay_data)
            except Exception as e:
                print(f"Error processing {essay_file}: {e}")
    
    # Sort essays by date (newest first)
    essays.sort(key=lambda x: datetime.strptime(x['date'], '%B %d, %Y'), reverse=True)
    
    # Generate index page with recent essays
    index_template = env.get_template('index.html')
    output = index_template.render(recent_essays=essays[:3])
    with open('docs/index.html', 'w', encoding='utf-8') as f:
        f.write(output)
    
    # Generate writing index page
    writing_template = env.get_template('writing.html')
    output = writing_template.render(essays=essays)
    with open('docs/writing.html', 'w', encoding='utf-8') as f:
        f.write(output)
    
    # Generate individual essay pages
    essay_template = env.get_template('essay.html')
    for essay in essays:
        output = essay_template.render(essay=essay)
        with open(f"docs/essays/{essay['slug']}.html", 'w', encoding='utf-8') as f:
            f.write(output)
    
    # Optional: Generate RSS feed
    # generate_rss_feed(essays)
    
    print(f"Built {len(essays)} essays")
    print("Site built successfully!")

def generate_rss_feed(essays):
    """Generate RSS feed from essays"""
    # This is a placeholder for RSS feed generation
    # Would need additional dependencies like feedgen
    pass

if __name__ == '__main__':
    build_site()