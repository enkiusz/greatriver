#!/usr/bin/env python3

import sys
import argparse
import random
import string
from structlog import get_logger
from pathlib import Path
from candybar.CandyBarCode128 import CandyBar128
import os
import io
import json
from PIL import Image, ImageFont, ImageDraw

import brother_ql.backends
import brother_ql.backends.helpers
import brother_ql.conversion
import brother_ql.devicedependent
from brother_ql.raster import BrotherQLRaster

log = get_logger()

def generate_code128(txt, width=600, height=60):
    cb128 = CandyBar128('', width, height)
    code = cb128.generate_barcode_with_contents(f'{txt}')
    return code

def generate_label(id1, id2=None):
    # 800 x 300 label
    label = Image.new(mode='RGB', size=(696, 271), color=(255,255,255))
    ctx = ImageDraw.Draw(label)
    font = ImageFont.truetype(font='Courier New', size=40)

    gap = 5
    x = 50
    y = 30
    
    id = id1
    code = generate_code128(id)
    code_img = Image.open(io.BytesIO(code))
    label.paste(code_img, box=(x,y))
    y += code_img.size[1] + gap

    # get the line size
    text_width, text_height = font.getsize(id)

    ctx.text((label.size[0]/2,y), id, font=font, anchor='ma', fill='black')
    y += text_height + gap

    ctx.line((0, y, label.size[0], y), fill='grey')

    y += gap*2

    if id2:
        id = id2
        code = generate_code128(id)
        code_img = Image.open(io.BytesIO(code))
        label.paste(code_img, box=(x,y))
        y += code_img.size[1] + gap


        # get the line size
        text_width, text_height = font.getsize(id)

        ctx.text((label.size[0]/2,y), id, font=font, anchor='ma', fill='black')
        y += text_height + gap

    return label

def new_cell(id, config, log):
    log.debug('creating cell')

    cell_path = Path(id)
    cell_path.mkdir(exist_ok=True)

    metadata = dict(v=0, id=id)

    if config.brand:
        metadata['brand'] = config.brand

    if config.model:
        metadata['model'] = config.model

    if config.capacity:
        metadata['capacity'] = { 'nom': config.capacity }

    if config.tags:
        metadata['tags'] = config.tags

    with open(cell_path.joinpath('meta.json'), "w") as f:
        f.write("V0\n")
        f.write(json.dumps(metadata, indent=2))

def main(config, log):

    if config.g:
        config.identifiers = [ f"C~{''.join(random.choices(string.digits, k=10))}" for i in range(config.g) ]

    if config.print_labels:
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
                line = line.rstrip()

                log = log.bind(id=line)
                new_cell(id=line, config=config, log=log)
                ids_processed.append(line)
        else:
            log = log.bind(id=id)
            new_cell(id=id, config=config, log=log)
            ids_processed.append(id)
        
    if config.print_labels:

        # 2 barcodes fit on a label
        batches = [ config.identifiers[i:i + 2] for i in range(0, len(config.identifiers), 2) ]
        labels = [ generate_label(b[0], b[1] if len(b)>1 else None) for b in batches ]
        
        log.debug('batches', batches=batches)
        log.debug('labels', labels=labels)

        if config.printer_pretend:
            for (i, image) in enumerate(labels):
                filename=f'labels_{i}.png'
                log.info('saving bitmap', file=filename)
                image.save(filename)
        else:
            qlr = BrotherQLRaster(config.printer_model)
            instructions = brother_ql.conversion.convert(qlr=qlr, images=labels, label=config.printer_label)
            brother_ql.backends.helpers.send(instructions=instructions, printer_identifier=config.printer_id, backend_identifier=config.printer_backend, blocking=True)
            
    print('\n'.join(ids_processed))

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Create new cells')
    parser.add_argument('-g', metavar='N', type=int, default=0, help='Number of cell identifiers to generate')
    parser.add_argument('-b', '--brand', help='Cell brand for all created cells')
    parser.add_argument('-m', '--model', help='Cell model for all created cells')
    parser.add_argument('-c', '--capacity', help='Capacity in mAh for all created cells')
    parser.add_argument('-P', '--print-labels', default=False, action='store_true', help='Print labels for the cells')
    parser.add_argument('-t', '--tag', dest='tags', action='append', help='Tag all created cells')
    parser.add_argument('--printer-model', metavar='MODEL', default=os.getenv('BROTHER_QL_MODEL'), 
        choices=brother_ql.devicedependent.models, help='Select the printer model for brother_ql')
    parser.add_argument('--printer-id', metavar='PRINTER_ID', default=os.getenv('BROTHER_QL_PRINTER'),
        help='Identifier string specifying the printer. If not specified, selects the first detected device.')
    parser.add_argument('--printer-backend', metavar='BACKEND', default=os.getenv('BROTHER_QL_BACKEND', 'pyusb'), 
        choices=brother_ql.backends.available_backends, help='Select the printer backend for brother_ql')
    parser.add_argument('--printer-label', default=os.getenv('BROTHER_QL_LABEL'), 
        choices=brother_ql.devicedependent.label_sizes, help='Select label size for brother_ql')
    parser.add_argument('--printer-pretend', action='store_true', default=False, help='Just pretend to print labels')
    parser.add_argument('identifiers', nargs='*', help='Cell identifiers, use - to read from stdin')

    args = parser.parse_args()
    log.debug('config', args=args)

    main(config=args, log=log)


