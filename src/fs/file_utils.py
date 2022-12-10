class FileUtils:

    @classmethod
    def get_content_from_byte_array(cls, data: bytearray) -> str:
        """

        :rtype: object
        """
        result = data.decode('utf-8').strip().rstrip('\x00')
        return str(result)
