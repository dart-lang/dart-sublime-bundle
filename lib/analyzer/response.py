"""Responses from the analyzer.
"""

import sublime


class StatusInfo(object):
    def __init__(self, data):
        self.data = data

    @property
    def is_analyzing(self):
        return self.data['params']['analysis']['analyzing']

    @property
    def message(self):
        if self.is_analyzing:
            return "Analysis started"
        return "Analysis finished"


class NewId(object):
    def __init__(self, data):
        self.data = data

    def __str__(self):
        return self.data['result']['id']

    @property
    def id(self):
        return self.data['result']['id']


class ErrorInfoCollection(object):
    def __init__(self, data):
        self.data = data
        self._errors = []
        self._warnings = []
        self._infos = []

    def __len__(self):
        return len(self.data['params']['errors'])

    @property
    def file(self):
        return self.data['params']['file']

    def errors_to_regions(self, view):
        for ei in self.errors:
            yield ei.to_region(view)

    def warnings_to_regions(self, view):
        for ei in self.warnings:
            yield ei.to_region(view)

    def infos_to_regions(self, view):
        for ei in self.infos:
            yield ei.to_region(view)

    @property
    def errors(self):
        if self._errors:
            yield from self._errors

        for err in  self.data['params']['errors']:
            ei = ErrorInfo(err)
            if ei.severity == 'ERROR':
                self._errors.append(ei)
                yield ei
            elif ei.severity == 'WARNING':
                self._warnings.append(ei)
            elif ei.severity == 'INFO':
                self._infos.append(ei)

    @property
    def warnings(self):
        if self._warnings:
            yield from self._warnings

        for err in  self.data['params']['errors']:
            ei = ErrorInfo(err)
            if ei.severity == 'WARNING':
                self._warnings.append(ei)
                yield ei
            elif ei.severity == 'ERROR':
                self._errors.append(ei)
            elif ei.severity == 'INFO':
                self._infos.append(ei)

    @property
    def infos(self):
        if self._warnings:
            yield from self._warnings

        for err in  self.data['params']['errors']:
            ei = ErrorInfo(err)
            if ei.severity == 'INFO':
                self._infos.append(ei)
                yield ei
            elif ei.severity == 'ERROR':
                self._errors.append(ei)
            elif ei.severity == 'WARNING':
                self._warnings.append(ei)

    def to_compact_text(self):
        # Make sure we populate the items cache.
        self.infos

        everything = sorted(self._errors + self._warnings + self._infos,
                            key=lambda x: x.offset)
        yield from (item.to_compact_text() for item in everything)



class ErrorInfo(object):
    def __init__(self, data):
        self.data = data

    def __str__(self):
        return "{self.severity}|{self.type}|{self.file}|{self.row}|{self.column}".format(self=self)

    @property
    def location(self):
        self.data['location']

    @property
    def severity(self):
        return self.data['severity']

    @property
    def type(self):
        return self.data['type']

    @property
    def file(self):
        return self.data['location']['file']

    @property
    def offset(self):
        return self.data['location']['offset']

    @property
    def length(self):
        return self.data['location']['length']

    @property
    def row(self):
        return self.data['location']['startLine']

    @property
    def column(self):
        return self.data['location']['startColumn']

    @property
    def message(self):
        return self.data['message']

    def to_region(self, view):
        pt = view.text_point(self.row - 1, self.column - 1)
        return sublime.Region(pt, pt + self.length)

    def to_compact_text(self):
        return "{self.severity}|{self.type}|{self.file}|{self.row}|{self.column}|{self.message}".format(self=self)


class Response(object):
    def __init__(self, data):
        self.data = data

    @property
    def id(self):
        return self.data['id']

    @property
    def type(self):
        return self.data.get('event', '<unknown>')

    @property
    def file(self):
        return self.data.get('file', None)

    @property
    def has_errors(self):
        return (self.data.get('event') == 'analysis.errors')

    @property
    def errors(self):
        if self.has_errors:
            return ErrorInfoCollection(self.data)

    @property
    def has_status(self):
        if self.data.get('event') == 'server.status':
            return True

    @property
    def status(self):
         if self.has_status:
            return StatusInfo(self.data)

    @property
    def has_new_id(self):
        return 'id' in self.data.get('result', {})

    @property
    def new_id(self):
        return NewId(self.data)

    @property
    def search_results(self):
        if self.type != "search.results":
            raise TypeError('not search results: %s', self.type)
        return SearchResults(self.data)


class SearchResults(object):
    #     notification: {
    #   "event": "search.results"
    #   "params": {
    #     "id": SearchId
    #     "results": List<SearchResult>
    #     "last": bool
    #   }
    # }
    def __init__(self, data):
        self.data = data

    def __str__(self):
        return str(self.data)

    @property
    def id(self):
        return self.data['params']['id']

    @property
    def results(self):
        return self.data['params']['results']

    @property
    def last(self):
        return self.data['params']['last']