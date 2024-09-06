import zlib
import nbt


FILENAME = "./region/r.0.0.mca"

def bytes_to_int(byte_string):
  return int.from_bytes(byte_string, "big")


class Region:
  SECTOR_SIZE = 4096
  def __init__(self, file):
    self.header = file[:8191] #in the format []
    self.chunk_data = file[8192:]
    self.chunks = []
    self._initialize_chunks()

  def _initialize_chunks(self):
    header_table_one = self.header[:Region.SECTOR_SIZE - 1]
    header_table_two = self.header[Region.SECTOR_SIZE:]
    parsed_header = [
      [
        bytes_to_int(header_table_one[i:i+3]) * Region.SECTOR_SIZE,
        bytes_to_int(header_table_one[i+3:i+4]) * Region.SECTOR_SIZE,
      ] for i in range(0, len(header_table_one), 4)
    ]

    timestamp_header = [
      [bytes_to_int(header_table_two[i:i+4])] for i in \
        range(0, len(header_table_two), 4)
    ]
    stitched_headers = [x + y for x, y in zip(parsed_header, timestamp_header)]

    chunk_payload = []
    for i in parsed_header:
      chunk_payload.append(
        self.chunk_data[
          i[0] - (2 * Region.SECTOR_SIZE):
          i[0] - (2 * Region.SECTOR_SIZE) + i[1]
        ]
      )

    stitched_headers = [
      x + [y] for x, y in zip(stitched_headers, chunk_payload)
    ]


    for entry in stitched_headers:
      chunk = self.Chunk(entry)
      self.chunks.append(chunk)

  def get_chunks(self):
    return self.chunks

  def get_chunk(self, x, z):
    chunk_index = x + (32 * z)
    return self.chunks[chunk_index]

  class Chunk:
    """
    Represents a chunk of data with its metadata, including offset, length, 
    and timestamp. 
    The chunk data is optionally decompressed if its length is a multiple of 
    `Region.SECTOR_SIZE`.

    Attributes:
        offset (int): The starting offset of the chunk in the region file.
        length (int): The length of the chunk data in bytes.
        timestamp (int): The timestamp when the chunk was last updated.
        chunk_data (bytes or None): The decompressed chunk data if valid, 
        otherwise None.
    """

    def __init__(self, header_data):
      #in the format []
      self.offset = header_data[0]
      self.length = header_data[1] #length in bytes
      self.timestamp = header_data[2]
      if len(header_data[3]) % Region.SECTOR_SIZE == 0 \
        and len(header_data[3]) > 0:
        self.chunk_data = zlib.decompress(header_data[3][5:])
      else:
        self.chunk_data = None

    def __str__(self) -> str:
      return str({
        "offset": self.offset,
        "length": self.length,
        "timestamp": self.timestamp
      })

    def data(self) -> bytes:
      return self.chunk_data


with open(FILENAME, "rb") as f:
  region = Region(f.read())
  print(region.get_chunk(1, 0).data()[0:100])
  filestring = region.get_chunk(0, 0).data().split(b"\n")
  print(filestring[5], filestring[7])

















# with open(FILENAME, "rb") as f:
#   r_header = f.read(4096)
#   r_header = [
#     [
#       bytes_to_int(
#         r_header[i:i+3]
#       ),
#       bytes_to_int(
#         r_header[i+3:i+4]
#       )
#     ]
#     for i in range(0, len(r_header), 4)
#   ]
#   file_header = f.read(4096)
#   file_header =  [
#     [
#       bytes_to_int(
#         file_header[i:i+4]
#       )
#     ]
#     for i in range(0, len(file_header), 4)
#   ]
#   region_header = [x + y for x, y in zip(r_header, file_header)]
#   print(region_header[:10])
