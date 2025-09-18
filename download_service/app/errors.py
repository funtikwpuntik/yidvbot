class AgeRestrictionError(Exception):
    __default_msg__ = "Couldn't download the video.\nAge limit."

    def __init__(self, video_id=None):
        msg = f"{self.__default_msg__}: {video_id}" if video_id else self.__default_msg__
        super().__init__(msg)


class VideoUnavailableError(Exception):
    __default_msg__ = "Couldn't download the video.\nThe video is unavailable."

    def __init__(self, video_id=None):
        msg = f"{self.__default_msg__}: {video_id}" if video_id else self.__default_msg__
        super().__init__(msg)


class FormatNotAvailableError(Exception):
    __default_msg__ = "Couldn't download the video."

    def __init__(self, video_id=None):
        msg = f"{self.__default_msg__}: {video_id}" if video_id else self.__default_msg__
        super().__init__(msg)


class GeoRestrictedError(Exception):
    __default_msg__ = "Couldn't download the video."

    def __init__(self, video_id=None):
        msg = f"{self.__default_msg__}: {video_id}" if video_id else self.__default_msg__
        super().__init__(msg)
