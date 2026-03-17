class MetadataBuilder:

    def build_metadata(self, filename, page_number, chunk_index=None):
        metadata = {
            "filename": filename,
            "page": page_number,
            "source": f"{filename}, trang {page_number}"
        }
        if chunk_index is not None:
            metadata["chunk_index"] = chunk_index
        return metadata