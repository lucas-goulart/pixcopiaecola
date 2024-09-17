from payload import PixPayload



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
