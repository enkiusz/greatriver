#!/usr/bin/env python3

# Allow module load from lib/python in main repo
import sys
from pathlib import Path
currentdir = Path(__file__).resolve(strict=True).parent
libdir = currentdir.parent.joinpath('lib/python')
sys.path.append(str(libdir))

import argparse
import random
import string
from structlog import get_logger
from candybar.CandyBarCode128 import CandyBar128
import os
import io
from PIL import Image, ImageFont, ImageDraw

import brother_ql.backends
import brother_ql.backends.helpers
import brother_ql.conversion
import brother_ql.devicedependent
from brother_ql.raster import BrotherQLRaster

from secondlife.cli.utils import generate_id

log = get_logger()


def generate_code128(txt, width=566, height=60):
    cb128 = CandyBar128('', width, height)
    code = cb128.generate_barcode_with_contents(f'{txt}')
    return code


def format_digits(s):
    out = str()
    while len(s) > 4:
        out += s[0:3]
        out += ' '
        s = s[3:]

    out += s
    return out


def generate_label(id1, id2=None):
    # 62x29 -> 696 x  271 usable area
    # 17x54 -> 165 x  566
    label = Image.new(mode='RGB', size=(566, 165), color=(255, 255, 255))
    ctx = ImageDraw.Draw(label)
    try:
        font = ImageFont.truetype(font='Courier New', size=40)
    except Excepton as e:
        font = ImageFont.truetype(font='UbuntuMono-R', size=40)

    gap = 5
    x = 0
    y = 30

    id = id1
    code = generate_code128(id)
    code_img = Image.open(io.BytesIO(code))
    label.paste(code_img, box=(x, y))
    y += code_img.size[1] + gap

    (code, num) = id.split('~')
    id_text = f'{code}~{format_digits(num)}'

    # get the line size
    text_width, text_height = font.getsize(id_text)

    ctx.text((label.size[0] / 2, y), id_text, font=font, anchor='ma', fill='black')
    y += text_height + gap * 2

    if id2:
        ctx.line((0, y, label.size[0], y), fill='grey')

        y += gap * 2

        id = id2
        code = generate_code128(id)
        code_img = Image.open(io.BytesIO(code))
        label.paste(code_img, box=(x, y))
        y += code_img.size[1] + gap

        # get the line size
        text_width, text_height = font.getsize(id)

        ctx.text((label.size[0] / 2, y), id, font=font, anchor='ma', fill='black')
        y += text_height + gap

    return label


def main(config, log):

    if config.g:
        config.identifiers = [ generate_id(config.prefix, k=config.size) for i in range(config.g) ]

    if not config.printer_pretend:
        if not config.printer_id:
            available_devices = brother_ql.backends.helpers.discover(backend_identifier=config.printer_backend)
            if not available_devices:
                sys.exit("No printers found")

            config.printer_id = available_devices[0]['identifier']
            log.info('autoselected printer', printer=config.printer_id)

    ids_processed = []

    for id in config.identifiers:

        if id == '-':
            for line in sys.stdin:
                line = line.strip()
                if len(line) == 0:
                    continue
                ids_processed.append(line)
        else:
            ids_processed.append(id)

    labels = [ generate_label(id) for id in ids_processed ]

    if config.printer_pretend:
        for (i, image) in enumerate(labels):
            filename = f'labels_{i}.png'
            log.info('saving bitmap', file=filename)
            image.save(filename)
    else:
        qlr = BrotherQLRaster(config.printer_model)
        instructions = brother_ql.conversion.convert(qlr=qlr, images=labels, label=config.printer_label)
        brother_ql.backends.helpers.send(instructions=instructions, printer_identifier=config.printer_id,
            backend_identifier=config.printer_backend, blocking=True)

    print('\n'.join(ids_processed))


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Generate new cell identifiers and print labels for them')
    parser.add_argument('-g', metavar='N', type=int, default=0, help='Number of cell identifiers to generate')
    parser.add_argument('--prefix', default='C', help='Prefix before the tilde character ~')
    parser.add_argument('--size', type=int, default=10, help='Number of digits after the tilde character ~')
    parser.add_argument('--printer-model', metavar='MODEL', default=os.getenv('BROTHER_QL_MODEL'),
        choices=brother_ql.devicedependent.models, help='Select the printer model for brother_ql')
    parser.add_argument('--printer-id', metavar='PRINTER_ID', default=os.getenv('BROTHER_QL_PRINTER'),
        help='Identifier string specifying the printer. If not specified, selects the first detected device.')
    parser.add_argument('--printer-backend', metavar='BACKEND', default=os.getenv('BROTHER_QL_BACKEND', 'pyusb'),
        choices=brother_ql.backends.available_backends, help='Select the printer backend for brother_ql')
    parser.add_argument('--printer-label', default=os.getenv('BROTHER_QL_LABEL'),
        choices=brother_ql.devicedependent.label_sizes, help='Select label size for brother_ql')
    parser.add_argument('--printer-pretend', action='store_true', default=False, help='Just pretend to print labels')
    parser.add_argument('identifiers', nargs='*', default=['-'], help='Cell identifiers, read from stdin by default')

    args = parser.parse_args()
    log.debug('config', args=args)

    main(config=args, log=log)
