from abc import abstractmethod
from xml.etree.ElementTree import Element, SubElement, tostring
from uuid import uuid4
import os

from model.match import Match

# Matches 전체 저장
class HighlightSaveAll:
    @staticmethod
    def save_highlights(matches: list[Match], file_path: [str, str]) -> bool:
        try:
            base = os.path.splitext(file_path)[0]
            for match in matches:
                match_id = match.get_match_id()
                file_dir = f"{base}_{match_id}"
                HighlightSaveXml().save(match, file_dir + ".xml")
                HighlightSaveTxt().save(match, file_dir + ".txt")
            return True

        except Exception as e:
            print(f"Error saving highlights to {file_path}: {e}")
            return False


# Match 객체 저장 인터페이스와 구현체
class IHighlightSave:
    @abstractmethod
    def save(self, highlights, file_path: str) -> None:
        pass


class HighlightSaveTxt(IHighlightSave):
    def save(self, match: Match, file_path: str) -> None:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                for highlight in match.get_highlights():
                    f.write(f"{highlight.to_display_string()}\n")
        except Exception as e:
            print(f"Error saving highlights to {file_path}: {e}")
            raise

class HighlightSaveXml(IHighlightSave):
    def save(self, match: Match, file_path: str) -> None:
        try:
            root = self.__make_xml(match)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(tostring(root, encoding='unicode'))
        except Exception as e:
            print(f"Error saving highlights to {file_path}: {e}")
            raise

    def __make_xml(self, match: Match) -> Element:
        try:
            highlights = match.get_highlights()
            match_id = match.get_match_id()
            root = Element("xmeml")
            root.set("version", "4")
            sequence = SubElement(root, "sequence", {
                "id": f"sequence_{match_id}",
                "TL.SQAudioVisibleBase": "0",
                "TL.SQVideoVisibleBase": "0",
                "TL.SQVisibleBaseTime": "0",
                "TL.SQAVDividerPosition": "0.5",
                "TL.SQHideShyTracks": "0",
                "TL.SQHeaderWidth": "292",
                "Monitor.ProgramZoomOut": "0",
                "Monitor.ProgramZoomIn": "0",
                "TL.SQTimePerPixel": "0.2",
                "MZ.EditLine": "0",
                "MZ.Sequence.PreviewFrameSizeHeight": "1080",
                "MZ.Sequence.PreviewFrameSizeWidth": "1920",
                "MZ.Sequence.AudioTimeDisplayFormat": "200",
                "MZ.Sequence.PreviewRenderingClassID": "1061109567",
                "MZ.Sequence.PreviewRenderingPresetCodec": "1634755439",
                "MZ.Sequence.PreviewRenderingPresetPath": "EncoderPresets/SequencePreview/795454d9-d3c2-429d-9474-923ab13b7018/QuickTime.epr",
                "MZ.Sequence.PreviewUseMaxRenderQuality": "false",
                "MZ.Sequence.PreviewUseMaxBitDepth": "false",
                "MZ.Sequence.EditingModeGUID": "795454d9-d3c2-429d-9474-923ab13b7018",
                "MZ.Sequence.VideoTimeDisplayFormat": "101",
                "MZ.WorkOutPoint": "4612930560000",
                "MZ.WorkInPoint": "0",
                "explodedTracks": "true"
            })
            SubElement(sequence, "uuid").text = str(uuid4())
            max_duration = max((h.end_time for h in highlights), default=1)
            SubElement(sequence, "duration").text = str(int(max_duration * 60))
            rate = SubElement(sequence, "rate")
            SubElement(rate, "timebase").text = "60"
            SubElement(rate, "ntsc").text = "FALSE"
            SubElement(sequence, "name").text = f"Marker - (Match {match_id})"
            media = SubElement(sequence, "media")
            video = SubElement(media, "video")
            format_elem = SubElement(video, "format")
            samplecharacteristics = SubElement(format_elem, "samplecharacteristics")
            rate = SubElement(samplecharacteristics, "rate")
            SubElement(rate, "timebase").text = "60"
            SubElement(rate, "ntsc").text = "FALSE"
            codec = SubElement(samplecharacteristics, "codec")
            SubElement(codec, "name").text = "Apple ProRes 422"
            appspecificdata = SubElement(codec, "appspecificdata")
            SubElement(appspecificdata, "appname").text = "Final Cut Pro"
            SubElement(appspecificdata, "appmanufacturer").text = "Apple Inc."
            SubElement(appspecificdata, "appversion").text = "7.0"
            data = SubElement(appspecificdata, "data")
            qtcodec = SubElement(data, "qtcodec")
            SubElement(qtcodec, "codecname").text = "Apple ProRes 422"
            SubElement(qtcodec, "codectypename").text = "Apple ProRes 422"
            SubElement(qtcodec, "codectypecode").text = "apcn"
            SubElement(qtcodec, "codecvendorcode").text = "appl"
            SubElement(qtcodec, "spatialquality").text = "1024"
            SubElement(qtcodec, "temporalquality").text = "0"
            SubElement(qtcodec, "keyframerate").text = "0"
            SubElement(qtcodec, "datarate").text = "0"
            SubElement(samplecharacteristics, "width").text = "1920"
            SubElement(samplecharacteristics, "height").text = "1080"
            SubElement(samplecharacteristics, "anamorphic").text = "FALSE"
            SubElement(samplecharacteristics, "pixelaspectratio").text = "square"
            SubElement(samplecharacteristics, "fielddominance").text = "none"
            SubElement(samplecharacteristics, "colordepth").text = "24"
            track = SubElement(video, "track", {
                "TL.SQTrackShy": "0",
                "TL.SQTrackExpandedHeight": "25",
                "TL.SQTrackExpanded": "0",
                "MZ.TrackTargeted": "0"
            })
            SubElement(track, "enabled").text = "TRUE"
            SubElement(track, "locked").text = "FALSE"
            generatoritem = SubElement(track, "generatoritem", {"id": f"generatoritem_{match_id}"})
            SubElement(generatoritem, "name").text = f"Marker Color Matte (Match {match_id})"
            SubElement(generatoritem, "enabled").text = "TRUE"
            SubElement(generatoritem, "duration").text = str(int(max_duration * 60))
            rate = SubElement(generatoritem, "rate")
            SubElement(rate, "timebase").text = "60"
            SubElement(rate, "ntsc").text = "FALSE"
            SubElement(generatoritem, "start").text = "0"
            SubElement(generatoritem, "end").text = str(int(max_duration * 60))
            SubElement(generatoritem, "in").text = "0"
            SubElement(generatoritem, "out").text = str(int(max_duration * 60))
            SubElement(generatoritem, "alphatype").text = "none"
            effect = SubElement(generatoritem, "effect")
            SubElement(effect, "name").text = "Color"
            SubElement(effect, "effectid").text = "Color"
            SubElement(effect, "effectcategory").text = "Matte"
            SubElement(effect, "effecttype").text = "generator"
            SubElement(effect, "mediatype").text = "video"
            parameter = SubElement(effect, "parameter", {"authoringApp": "PremierePro"})
            SubElement(parameter, "parameterid").text = "fillcolor"
            SubElement(parameter, "name").text = "Color"
            value = SubElement(parameter, "value")
            SubElement(value, "alpha").text = "0"
            SubElement(value, "red").text = "0"
            SubElement(value, "green").text = "0"
            SubElement(value, "blue").text = "0"
            filter = SubElement(generatoritem, "filter")
            effect = SubElement(filter, "effect")
            SubElement(effect, "name").text = "Opacity"
            SubElement(effect, "effectid").text = "opacity"
            SubElement(effect, "effectcategory").text = "motion"
            SubElement(effect, "effecttype").text = "motion"
            SubElement(effect, "mediatype").text = "video"
            SubElement(effect, "pproBypass").text = "false"
            parameter = SubElement(effect, "parameter", {"authoringApp": "PremierePro"})
            SubElement(parameter, "parameterid").text = "opacity"
            SubElement(parameter, "name").text = "opacity"
            SubElement(parameter, "valuemin").text = "0"
            SubElement(parameter, "valuemax").text = "100"
            SubElement(parameter, "value").text = "0"
            seen_in_values = set()
            for i, h in enumerate(highlights):
                in_value = int(h.start_time * 60)
                out_value = int(h.end_time * 60)
                if in_value >= out_value:
                    out_value = in_value + 60
                while in_value in seen_in_values:
                    in_value += 1
                    out_value += 1
                seen_in_values.add(in_value)
                marker = SubElement(generatoritem, "marker")
                SubElement(marker, "comment").text = h.memo
                SubElement(marker, "name").text = ""
                SubElement(marker, "in").text = str(in_value)
                SubElement(marker, "out").text = str(out_value)
                SubElement(marker, "pproColor").text = "4294741314"
            timecode = SubElement(sequence, "timecode")
            rate = SubElement(timecode, "rate")
            SubElement(rate, "timebase").text = "60"
            SubElement(rate, "ntsc").text = "FALSE"
            SubElement(timecode, "string").text = "00:00:00:00"
            SubElement(timecode, "frame").text = "0"
            SubElement(timecode, "displayformat").text = "NDF"
            labels = SubElement(sequence, "labels")
            SubElement(labels, "label2").text = "Iris"
            logginginfo = SubElement(sequence, "logginginfo")
            SubElement(logginginfo, "description").text = ""
            SubElement(logginginfo, "scene").text = ""
            SubElement(logginginfo, "shottake").text = ""
            SubElement(logginginfo, "lognote").text = ""
            SubElement(logginginfo, "good").text = ""
            SubElement(logginginfo, "originalvideofilename").text = ""
            SubElement(logginginfo, "originalaudiofilename").text = ""
            seen_in_values.clear()
            for i, h in enumerate(highlights):
                in_value = int(h.start_time * 60)
                out_value = int(h.end_time * 60)
                if in_value >= out_value:
                    out_value = in_value + 60
                while in_value in seen_in_values:
                    in_value += 1
                    out_value += 1
                seen_in_values.add(in_value)
                marker = SubElement(sequence, "marker")
                SubElement(marker, "comment").text = h.memo
                SubElement(marker, "name").text = ""
                SubElement(marker, "in").text = str(in_value)
                SubElement(marker, "out").text = str(out_value)
                SubElement(marker, "pproColor").text = "4294741314"
            return root
        except Exception as e:
            print(f"Error creating XML: {e}")
            raise
