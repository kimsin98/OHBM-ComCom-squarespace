#!/usr/bin/env python
# coding: utf-8
"""
Extract content from html, clean it, and save the results by year/date.
"""
import argparse
from pathlib import Path

from lxml import html
from cssutils import parseStyle
from datetime import datetime

import json
import shutil

BLOCK_TAGS = ['div', 'ul', 'ol', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
              'blockquote', 'table', 'pre', 'div']
SEQUENTIAL_TAGS = ['li', 'tr', 'td']
DEFAULT_TAGS = ['p', 'div', 'span']
DEFAULT_STYLES = {
    'color': ['black', 'rgb(0, 0, 0)', '#000'],
    'font-weight': ['normal', '400'],
    'text-align': ['left']
}


class Trait:
    def __init__(self, element):
        self.tag = element.tag

        # unique traits
        if self.tag in BLOCK_TAGS + SEQUENTIAL_TAGS:
            self.element = element
        else:
            self.element = None

        # remove default CSS styles
        if self.tag in DEFAULT_TAGS and 'style' in element.attrib:
            style = parseStyle(element.attrib['style'])
            for prop in style:
                if (prop.name in DEFAULT_STYLES and
                        prop.value in DEFAULT_STYLES[prop.name]):
                    style.removeProperty(prop.name)
            if style.keys():
                element.attrib['style'] = style.getCssText(' ')
            else:
                del element.attrib['style']
        self.attrib = element.attrib
        return

    def __eq__(self, other):
        return (self.tag == other.tag and self.attrib == other.attrib
                and self.element == other.element)

    def __bool__(self):
        return self.tag not in DEFAULT_TAGS or bool(self.attrib)

    def create_element(self):
        return html.Element(self.tag, attrib=self.attrib)


def collect_traits(text, root):
    if isinstance(text, html.HtmlElement) or text.is_text:
        element = text.getparent()
    elif text.is_tail:
        element = text.getparent().getparent()

    traits = []
    while element != root and element.tag not in BLOCK_TAGS:
        trait = Trait(element)
        if trait:
            traits.insert(0, trait)
        element = element.getparent()
    # always add top
    traits.insert(0, Trait(element))

    return traits


def create_by_traits(traits):
    branch = []
    for t in traits:
        element = t.create_element()
        if branch:
            branch[-1].append(element)
        branch.append(element)
    return branch


def first_diff_at(a, b):
    min_len = min(len(a), len(b))
    for i in range(min_len):
        if a[i] != b[i]:
            return i
    if len(a) != len(b):
        return min_len
    return None


def append_text_to(element, text):
    if isinstance(text, html.HtmlElement):
        element.append(html.Element(text.tag, attrib=text.attrib))
    else:
        children = list(element)
        if children:
            children[-1].tail = (children[-1].tail or '') + text
        else:
            element.text = (element.text or '') + text


def rebuild_trees(trees):
    rebuilt = []
    for tree in trees:
        textbrs = tree.xpath('.//text() | .//br')

        # keep single <br/> between text only
        texts = []
        br_start = None
        for i, t in enumerate(textbrs):
            if isinstance(t, html.HtmlElement):
                if br_start is None:
                    br_start = i
                continue

            if br_start:
                # cut if 2+ <br/>
                if i - br_start > 1:
                    texts.append(None)
                else:
                    texts.append(textbrs[br_start])
                br_start = None

            texts.append(t)

        # build new <p>s
        cur_branch, cur_traits = None, None
        for t in texts:
            if t is None:
                rebuilt.append(cur_branch[0])
                cur_branch, cur_traits = None, None
                continue

            traits = collect_traits(t, tree)

            # new branch
            if not cur_branch:
                cur_branch, cur_traits = create_by_traits(traits), traits
                append_text_to(cur_branch[-1], t)
                continue

            branch_at = first_diff_at(traits, cur_traits)

            # same branch
            if branch_at is None:
                append_text_to(cur_branch[-1], t)
                continue

            # restart branch
            if branch_at == 0:
                rebuilt.append(cur_branch[0])
                cur_branch, cur_traits = create_by_traits(traits), traits
                append_text_to(cur_branch[-1], t)
                continue

            # split branch
            if branch_at < len(cur_traits):
                cur_branch = cur_branch[:branch_at]
                cur_traits = cur_traits[:branch_at]
            if branch_at < len(traits):
                new_split = create_by_traits(traits[branch_at:])
                cur_branch[-1].append(new_split[0])
                cur_branch.extend(new_split)
                cur_traits.extend(traits[branch_at:])
            append_text_to(cur_branch[-1], t)

        if cur_branch is not None:
            rebuilt.append(cur_branch[0])

    return rebuilt


def extract_text(tree):
    blog = tree.find(".//div[@class='blog-content']")
    trees = []

    # author, subtitle
    author = blog.find(".//h2[@class='blog-author-title']")
    if author is not None:
        author.tag = 'p'
        author.attrib['class'] = 'sqsrte-large'
        trees.extend(rebuild_trees([author]))

        subtitle = author.getnext()
        if subtitle.tag == 'p':
            subtitle.attrib['class'] = 'sqsrte-text-color--accent'
            trees.extend(rebuild_trees([subtitle]))

    # main text
    paragraphs = blog.findall(".//div[@class='paragraph']")
    for paragraph in paragraphs:
        paragraph.tag = 'p'
        del paragraph.attrib['class']
    trees.extend(rebuild_trees(paragraphs))

    return trees


def extract_meta(tree):
    metadata = {
        'title': tree.find(".//meta[@property='og:title']").attrib['content'],
        'url': tree.find(".//meta[@property='og:url']").attrib['content']
    }

    date = tree.find(".//*[@class='date-text']")
    if date is not None:
        metadata['date'] = (datetime.strptime(date.text.strip(), '%m/%d/%Y')
                            .strftime('%Y-%m-%d'))

    blog = tree.find(".//div[@class='blog-content']")
    author = blog.find(".//*[@class='blog-author-title']")
    if author is not None:
        metadata['author'] = html.tostring(author, method='text',
                                           encoding='unicode').strip()

    return metadata


def get_image_paths(tree):
    images = tree.findall(".//meta[@property='og:image']")

    image_paths = []
    for image in images:
        url_path = Path(image.attrib['content'])
        image_paths.append(Path(*url_path.parts[1:]))

    return image_paths


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pattern', type=str, help='HTML files to process')
    parser.add_argument('out_dir', type=Path, help='Directory to save outputs')
    args = parser.parse_args()

    for file in Path('.').glob(args.pattern):
        print('Processing', file)
        tree = html.parse(file)

        # extract metadata
        meta = extract_meta(tree)
        date = datetime.strptime(meta['date'], '%Y-%m-%d')
        url_path = Path(meta['url'])
        directory = Path(datetime.strftime(date, '%Y/%m'), url_path.stem)
        (args.out_dir / directory).mkdir(parents=True, exist_ok=True)

        with open(args.out_dir / directory / 'metadata.json', 'w',
                  encoding='utf-8') as f:
            json.dump(meta, f, ensure_ascii=False, indent=4)

        # extract text
        with open(args.out_dir / directory / 'text.html', 'w',
                  encoding='utf-8') as f:
            for t in extract_text(tree):
                f.write(html.tostring(t, encoding='unicode'))
                f.write('\n')

        # copy images, report missing
        image_paths = get_image_paths(tree)
        missing = []
        for i in image_paths:
            if i.exists():
                shutil.copy2(i, args.out_dir / directory / i.name)
            elif 'placeholder' not in i.stem:
                print("can't find", i)
                missing.append(str(i))

        if missing:
            with open(args.out_dir / directory / 'MISSING.txt', 'w') as f:
                for m in missing:
                    f.write(m + '\n')


if __name__ == '__main__':
    main()
