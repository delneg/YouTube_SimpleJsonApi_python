import youtube.youtube_yapi as youtube_api
import isodate
import json
import logging

class ChannelNotFoundException(Exception):
    def __init__(self, channel_id):
        self.channel_id = channel_id
        self.message = 'No such channel or no videos on it - '+channel_id
        self.code = 1

class YoutubeVideo:
    def __init__(self, data):
        try:
            self.id = data.id.videoId
        except AttributeError:
            self.id = data.id
        self.channel_id = data.snippet.channelId
        self.channel_title = data.snippet.channelTitle
        self.description = data.snippet.description
        try:
            self.published_at = isodate.parse_datetime(data.snippet.published_at)
        except AttributeError:
            self.published_at = None
        self.title = data.snippet.title
        try:
            thumbnails = data.snippet.thumbnails
            try:
                self.thumbnail = thumbnails.high
            except AttributeError:
                try:
                    self.thumbnail = thumbnails.medium
                except AttributeError:
                    self.thumbnail = thumbnails.default
        except AttributeError:
            self.thumbnail = None
        try:
            statistics = data.statistics
            try:
                self.like_count = statistics.likeCount
            except AttributeError:
                self.like_count = None
            try:
                self.view_count = statistics.viewCount
            except AttributeError:
                self.view_count = None

        except AttributeError:
            self.like_count = None
            self.view_count = None

    def get_link(self):
        return 'https://www.youtube.com/watch?v=' + self.id

    def __dict__(self):
        try:
            thumbnail = self.thumbnail.url
        except AttributeError:
            thumbnail = ''
        return {
            'id': self.id,
            'channel_id':self.channel_id,
            'channel_title':self.channel_title,
            'description':self.description,
            'published_at':str(self.published_at) if self.published_at else '',
            'title':self.title,
            'thumbnail': thumbnail,
            'view_count': self.view_count if self.view_count else '',
            'like_count': self.like_count if self.like_count else ''
        }
class YoutubeVideoJson:
    '''
        Simple class to get YouTube public videos info in json
    '''

    def __init__(self, api_key, max_results=50):
        '''
        Initializes with YouTube v3 API key and max_results (0-50) as of December 2016
        :param api_key: YouTube v3 ApiKey
        :param max_results:  YouTube max_results
        '''
        self.api = youtube_api.YoutubeAPI(api_key)
        self.MAX_RESULTS = max_results

    def _get_channel_first(self, channel_id):
        '''
        Internal use function for getting initial channel videos data
        :param channel_id: Youtube channel id
        :return: videos(first self.MAX_RESULTS videos), page_token(next page token), pages (pages_count)
        '''
        if not isinstance(channel_id, str):
            msg = 'Channel id must be str, got ' + str(type(channel_id))
            logging.error(msg)
            raise TypeError(msg)

        videos_first = self.api.video_search_in_channel('', channel_id, order='date', max_results=self.MAX_RESULTS)
        if len(videos_first.items) == 0:
            return ChannelNotFoundException(channel_id)

        page_token = videos_first.nextPageToken
        pages = range((videos_first.pageInfo.totalResults - self.MAX_RESULTS) // self.MAX_RESULTS + 1)
        if self.MAX_RESULTS % videos_first.pageInfo.totalResults == 0:
            pages -= 1
        return videos_first, page_token, pages

    def _get_channel_videos_with_page_token(self,channel_id,page_token,pages):
        videos = []
        for i in pages:
            videos_current = self.api.video_search_in_channel('', channel_id, order='date', max_results=self.MAX_RESULTS,
                                                 page_token=page_token)
            videos+=videos_current.items
            try:
                page_token = videos_current.nextPageToken
            except AttributeError:
                pass
        return videos

    def get_channel_video_ids(self, channel_id):
        videos_first, page_token, pages = self._get_channel_first(channel_id)
        ids = [i.id.videoId for i in videos_first.items]
        [ids.append(j.id.videoId) for j in self._get_channel_videos_with_page_token(channel_id,page_token,pages)]
        return json.dumps(ids)

    def get_channel_videos_short_info(self, channel_id):
        videos_first, page_token, pages = self._get_channel_first(channel_id)
        videos = [YoutubeVideo(i).__dict__() for i in videos_first.items]
        [videos.append(YoutubeVideo(j).__dict__()) for j in self._get_channel_videos_with_page_token(channel_id,page_token,pages)]
        return json.dumps(videos)

    def get_channel_videos_full_info(self, channel_id):

        ids = json.loads(self.get_channel_video_ids(channel_id))
        logging.info('Got video ids for full ' + channel_id + ' info')
        videos = []
        for i in ids:

            v = self.api.get_video_info(i).items[0]
            videos.append(YoutubeVideo(v).__dict__())
        return json.dumps(videos)
