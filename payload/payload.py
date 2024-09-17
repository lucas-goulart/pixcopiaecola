import crcmod
import qrcode
import os
import base64
from io import BytesIO


class PixPayload:
    def __init__(self, name, pix_key, amount, city, txid, directory=''):
        """
        Initializes the PixPayload with the necessary information.

        :param name: Merchant's name
        :param pix_key: Pix key (email, phone number, etc.)
        :param amount: Transaction amount as a string (e.g., '1.00')
        :param city: Merchant's city
        :param txid: Transaction ID
        :param directory: Directory to save the QR code image (optional)
        """
        self.name: str = name
        self.pix_key: str  = pix_key
        self.amount: str  = amount.replace(',', '.')
        self.city: str  = city
        self.txid: str  = txid
        self.directory: str  = directory

        self.payload = None

        # Define fixed values for the payload
        self.payload_format_indicator = '000201'
        self.merchant_category_code = '52040000'
        self.transaction_currency = '5303986'  # Currency code 986 corresponds to BRL
        self.country_code = '5802BR'
        self.crc16_header = '6304'  # CRC16 header

    def generate_payload(self):
        """
        Generates the Pix payload string with CRC16 checksum.

        :return: The complete Pix payload string.
        """
        # Build the Merchant Account Information
        gui = '0014BR.GOV.BCB.PIX'
        key = f'01{len(self.pix_key):02}{self.pix_key}'
        merchant_account_info = f'{gui}{key}'
        merchant_account_info_field = f'26{len(merchant_account_info):02}{merchant_account_info}'

        # Format the Transaction Amount
        amount_formatted = f'{float(self.amount):.2f}'
        amount_field = f'54{len(amount_formatted):02}{amount_formatted}'

        # Build the Merchant Name field
        name_field = f'59{len(self.name):02}{self.name}'

        # Build the Merchant City field
        city_field = f'60{len(self.city):02}{self.city}'

        # Build the Additional Data Field Template (TXID)
        txid_field = f'05{len(self.txid):02}{self.txid}'
        additional_data_field = f'62{len(txid_field):02}{txid_field}'

        # Assemble the payload without the CRC16 checksum
        payload = (
                self.payload_format_indicator +
                merchant_account_info_field +
                self.merchant_category_code +
                self.transaction_currency +
                amount_field +
                self.country_code +
                name_field +
                city_field +
                additional_data_field +
                self.crc16_header
        )

        # Calculate and append the CRC16 checksum
        crc16_checksum = self._calculate_crc16(payload)
        self.payload = f'{payload}{crc16_checksum}'

        return self.payload

    @staticmethod
    def _calculate_crc16(payload):
        """
        Calculates the CRC16 checksum for the given payload.

        :param payload: The payload string without the CRC16 checksum.
        :return: The CRC16 checksum as a hexadecimal string.
        """
        crc16_func = crcmod.mkCrcFun(0x11021, initCrc=0xFFFF, rev=False, xorOut=0x0000)
        checksum = crc16_func(payload.encode('utf-8'))
        return f'{checksum:04X}'

    def save_qr_code(self, payload):
        """
        Generates and saves the QR code image of the Pix payload.

        :param payload: The Pix payload string.
        """
        directory = os.path.expanduser(self.directory)
        qr = qrcode.make(payload)
        file_path = os.path.join(directory, 'pix_qrcode.png')
        qr.save(file_path)
        print(f"QR code image saved at '{file_path}'.")

    @staticmethod
    def get_qr_code_base64(payload):
        """
        Generates the QR code image of the Pix payload and returns it as a base64 string.

        :param payload: The Pix payload string.
        :return: The base64-encoded string of the QR code image.
        """
        qr = qrcode.make(payload)
        buffered = BytesIO()
        qr.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        return img_base64


if __name__ == '__main__':
    # Create an instance of PixPayload with sample data
    pix_payload = PixPayload(
        name='John Doe',
        pix_key='12345678900',  # Example CPF without dots and dashes, if phoneNumber, use +55 and DDD ex +55249xxxxxxxx
        amount='1000.00',
        city='Sample City',
        txid='STORE01'
    )

    # Generate the payload string
    payload = pix_payload.generate_payload()
    print("Generated Payload:")
    print(payload)

    # Save the QR code image
    # pix_payload.save_qr_code(payload)

    # Get the QR code image as a base64 string (useful for sending to a frontend)
    qr_code_base64 = pix_payload.get_qr_code_base64(payload)
    print("QR Code Image as Base64 String:")
    print(qr_code_base64)
