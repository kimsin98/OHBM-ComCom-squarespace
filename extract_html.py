#!/usr/bin/env python
# coding: utf-8
"""
Extract content from html, clean it, and save the results by year/date.
"""
import argparse
from pathlib import Path
from lxml import html
from datetime import datetime
import json
import shutil


def collect_attribs(text):
    if text.is_text:
        element = text.getparent()
    elif text.is_tail:
        element = text.getparent().getparent()

    attribs = []
    while element.get('class') != 'paragraph':
        if element.tag != 'br':
            attribs.insert(0, (element.tag, dict(element.attrib)))
        element = element.getparent()

    # paragraph div -> p
    attrib = dict(element.attrib)
    del attrib['class']
    attribs.insert(0, ('p', attrib))

    return attribs


def create_by_attribs(attribs):
    branch = []
    for a in attribs:
        e = html.Element(a[0], attrib=a[1])
        if branch:
            branch[-1].append(e)
        branch.append(e)
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
    children = element.getchildren()
    if children:
        children[-1].tail = (children[-1].tail or '') + text
    else:
        element.text = (element.text or '') + text
    return


def extract_text(tree):
    blog = tree.find(".//div[@class='blog-content']")
    paragraphs = blog.findall(".//div[@class='paragraph']")

    ps = []
    for paragraph in paragraphs:
        cur_branch, cur_attribs = None, None
        consec_br = 0

        for t in paragraph.xpath('.//text() | .//br'):
            # <br/>
            if not isinstance(t, str):
                consec_br += 1
                continue

            # text
            if consec_br == 1 and cur_branch:
                cur_branch[-1].append(html.Element('br'))
            elif consec_br > 1 and cur_branch:
                ps.append(cur_branch[0])
                cur_branch, cur_attribs = None, None
            consec_br = 0

            attribs = collect_attribs(t)

            # new branch
            if not cur_branch:
                cur_branch, cur_attribs = create_by_attribs(attribs), attribs
                append_text_to(cur_branch[-1], t)
                continue

            branch_at = first_diff_at(attribs, cur_attribs)

            # same branch
            if branch_at is None:
                append_text_to(cur_branch[-1], t)
                continue

            # restart branch
            if branch_at == 0:
                ps.append(cur_branch[0])
                cur_branch, cur_attribs = create_by_attribs(attribs), attribs
                append_text_to(cur_branch[-1], t)
                continue

            # split branch
            if branch_at < len(cur_attribs):
                cur_branch = cur_branch[:branch_at]
                cur_attribs = cur_attribs[:branch_at]
            if branch_at < len(attribs):
                new_split = create_by_attribs(attribs[branch_at:])
                cur_branch[-1].append(new_split[0])
                cur_branch.extend(new_split)
                cur_attribs.extend(attribs[branch_at:])
            append_text_to(cur_branch[-1], t)

        if cur_branch is not None:
            ps.append(cur_branch[0])

    return ps


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
            for p in extract_text(tree):
                f.write(html.tostring(p, encoding='unicode'))
                f.write('\n')

        # copy images
        image_paths = get_image_paths(tree)
        for i in image_paths:
            if i.exists():
                shutil.copy2(i, args.out_dir / directory / i.name)
            else:
                print("can't find", i)


if __name__ == '__main__':
    main()
