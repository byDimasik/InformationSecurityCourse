import os

import lsb
import config


if __name__ == "__main__":
    lsb_ = lsb.LSB()

    lsb_.insertion(config.input_image_name, config.output_image_name, config.input_payload_file_name)
    lsb_.extract(config.output_image_name, config.output_payload_file_name)

    result = os.system(f'diff {config.input_payload_file_name} {config.output_payload_file_name} > /dev/null')

    if result != 0:
        print('Differences:', result)
    else:
        print('No differences')
