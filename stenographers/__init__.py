from abc import ABC, abstractmethod
import cv2


class SteganographyException(Exception):
    pass


class Stenograph(ABC):
    def __init__(self, input_file_name: str) -> None:
        super().__init__()

    def set_image(self, input_file_name):
        im = cv2.imread(input_file_name)
        self.image = im
        self.height, self.width, self.nbchannels = im.shape
        self.size = self.width * self.height

    @abstractmethod
    def encode(self, data: bytes):
        pass

    @abstractmethod
    def decode(self) -> bytes:
        pass

