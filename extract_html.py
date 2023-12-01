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
    if isinstance(text, html.HtmlElement) or text.is_text:
        element = text.getparent()
    elif text.is_tail:
        element = text.getparent().getparent()

    attribs = []
    while element.get('class') != 'paragraph':
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
    if isinstance(text, html.HtmlElement):
        element.append(html.Element(text.tag, attrib=text.attrib))
    else:
        children = list(element)
        if children:
            children[-1].tail = (children[-1].tail or '') + text
        else:
            element.text = (element.text or '') + text


def extract_text(tree):
    blog = tree.find(".//div[@class='blog-content']")
    paragraphs = blog.findall(".//div[@class='paragraph']")

    ps = []
    for paragraph in paragraphs:
        textbrs = paragraph.xpath('.//text() | .//br')

        # keep single <br/> between text only
        texts = []
        br_start = None
        for i, t in enumerate(textbrs):
            if not isinstance(t, str):
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
        cur_branch, cur_attribs = None, None
        for t in texts:
            if t is None:
                ps.append(cur_branch[0])
                cur_branch, cur_attribs = None, None
                continue

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
