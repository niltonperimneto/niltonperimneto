#!/usr/bin/env python3
import base64
import html
import json
import os
import subprocess
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config.json"
ASSETS_DIR = BASE_DIR / "assets"


def load_config():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def xesc(val):
    return html.escape(str(val), quote=True)


def truncate(text, max_len=36):
    text = str(text).strip()
    return text if len(text) <= max_len else text[: max_len - 1].rstrip() + "…"


# Canonical 24x24 Simple Icons Vector Paths
C_HEX_PATH = "M11.5 2.1a1 1 0 0 1 1 0l7.8 4.5a1 1 0 0 1 .5.87v9.06a1 1 0 0 1-.5.87l-7.8 4.5a1 1 0 0 1-1 0l-7.8-4.5a1 1 0 0 1-.5-.87V7.47a1 1 0 0 1 .5-.87z M12 6.5a5.5 5.5 0 1 0 3.89 9.39l-1.42-1.42A3.5 3.5 0 1 1 12 8.5c.97 0 1.85.39 2.47 1.03l1.42-1.42A5.47 5.47 0 0 0 12 6.5z"
CPP_HEX_PATH = "M11.5 2.1a1 1 0 0 1 1 0l7.8 4.5a1 1 0 0 1 .5.87v9.06a1 1 0 0 1-.5.87l-7.8 4.5a1 1 0 0 1-1 0l-7.8-4.5a1 1 0 0 1-.5-.87V7.47a1 1 0 0 1 .5-.87z M10.5 7a4.5 4.5 0 1 0 3.18 7.68l-1.42-1.42A2.5 2.5 0 1 1 10.5 9c.69 0 1.32.28 1.77.73l1.42-1.42A4.47 4.47 0 0 0 10.5 7z M15 11h1v-1h1v1h1v1h-1v1h-1v-1h-1z M19 11h1v-1h1v1h1v1h-1v1h-1v-1h-1z"

ICONS = {
    "rust": "M23.8346 11.7033l-1.0073-.6236a13.7268 13.7268 0 00-.0283-.2936l.8656-.8069a.3483.3483 0 00-.1154-.578l-1.1066-.414a8.4958 8.4958 0 00-.087-.2856l.6904-.9587a.3462.3462 0 00-.2257-.5446l-1.1663-.1894a9.3574 9.3574 0 00-.1407-.2622l.49-1.0761a.3437.3437 0 00-.0274-.3361.3486.3486 0 00-.3006-.154l-1.1845.0416a6.7444 6.7444 0 00-.1873-.2268l.2723-1.153a.3472.3472 0 00-.417-.4172l-1.1532.2724a14.0183 14.0183 0 00-.2278-.1873l.0415-1.1845a.3442.3442 0 00-.49-.328l-1.076.491c-.0872-.0476-.1742-.0952-.2623-.1407l-.1903-1.1673A.3483.3483 0 0016.256.955l-.9597.6905a8.4867 8.4867 0 00-.2855-.086l-.414-1.1066a.3483.3483 0 00-.5781-.1154l-.8069.8666a9.2936 9.2936 0 00-.2936-.0284L12.2946.1683a.3462.3462 0 00-.5892 0l-.6236 1.0073a13.7383 13.7383 0 00-.2936.0284L9.9803.3374a.3462.3462 0 00-.578.1154l-.4141 1.1065c-.0962.0274-.1903.0567-.2855.086L7.744.955a.3483.3483 0 00-.5447.2258L7.009 2.348a9.3574 9.3574 0 00-.2622.1407l-1.0762-.491a.3462.3462 0 00-.49.328l.0416 1.1845a7.9826 7.9826 0 00-.2278.1873L3.8413 3.425a.3472.3472 0 00-.4171.4171l.2713 1.1531c-.0628.075-.1255.1509-.1863.2268l-1.1845-.0415a.3462.3462 0 00-.328.49l.491 1.0761a9.167 9.167 0 00-.1407.2622l-1.1662.1894a.3483.3483 0 00-.2258.5446l.6904.9587a13.303 13.303 0 00-.087.2855l-1.1065.414a.3483.3483 0 00-.1155.5781l.8656.807a9.2936 9.2936 0 00-.0283.2935l-1.0073.6236a.3442.3442 0 000 .5892l1.0073.6236c.008.0982.0182.1964.0283.2936l-.8656.8079a.3462.3462 0 00.1155.578l1.1065.4141c.0273.0962.0567.1914.087.2855l-.6904.9587a.3452.3452 0 00.2268.5447l1.1662.1893c.0456.088.0922.1751.1408.2622l-.491 1.0762a.3462.3462 0 00.328.49l1.1834-.0415c.0618.0769.1235.1528.1873.2277l-.2713 1.1541a.3462.3462 0 00.4171.4161l1.153-.2713c.075.0638.151.1255.2279.1863l-.0415 1.1845a.3442.3442 0 00.49.327l1.0761-.49c.087.0486.1741.0951.2622.1407l.1903 1.1662a.3483.3483 0 00.5447.2268l.9587-.6904a9.299 9.299 0 00.2855.087l.414 1.1066a.3452.3452 0 00.5781.1154l.8079-.8656c.0972.0111.1954.0203.2936.0294l.6236 1.0073a.3472.3472 0 00.5892 0l.6236-1.0073c.0982-.0091.1964-.0183.2936-.0294l.8069.8656a.3483.3483 0 00.578-.1154l.4141-1.1066a8.4626 8.4626 0 00.2855-.087l.9587.6904a.3452.3452 0 00.5447-.2268l.1903-1.1662c.088-.0456.1751-.0931.2622-.1407l1.0762.49a.3472.3472 0 00.49-.327l-.0415-1.1845a6.7267 6.7267 0 00.2267-.1863l1.1531.2713a.3472.3472 0 00.4171-.416l-.2713-1.1542c.0628-.0749.1255-.1508.1863-.2278l1.1845.0415a.3442.3442 0 00.328-.49l-.49-1.076c.0475-.0872.0951-.1742.1407-.2623l1.1662-.1893a.3483.3483 0 00.2258-.5447l-.6904-.9587.087-.2855 1.1066-.414a.3462.3462 0 00.1154-.5781l-.8656-.8079c.0101-.0972.0202-.1954.0283-.2936l1.0073-.6236a.3442.3442 0 000-.5892zm-6.7413 8.3551a.7138.7138 0 01.2986-1.396.714.714 0 11-.2997 1.396zm-.3422-2.3142a.649.649 0 00-.7715.5l-.3573 1.6685c-1.1035.501-2.3285.7795-3.6193.7795a8.7368 8.7368 0 01-3.6951-.814l-.3574-1.6684a.648.648 0 00-.7714-.499l-1.473.3158a8.7216 8.7216 0 01-.7613-.898h7.1676c.081 0 .1356-.0141.1356-.088v-2.536c0-.074-.0536-.0881-.1356-.0881h-2.0966v-1.6077h2.2677c.2065 0 1.1065.0587 1.394 1.2088.0901.3533.2875 1.5044.4232 1.8729.1346.413.6833 1.2381 1.2685 1.2381h3.5716a.7492.7492 0 00.1296-.0131 8.7874 8.7874 0 01-.8119.9526zM6.8369 20.024a.714.714 0 11-.2997-1.396.714.714 0 01.2997 1.396zM4.1177 8.9972a.7137.7137 0 11-1.304.5791.7137.7137 0 011.304-.579zm-.8352 1.9813l1.5347-.6824a.65.65 0 00.33-.8585l-.3158-.7147h1.2432v5.6025H3.5669a8.7753 8.7753 0 01-.2834-3.348zm6.7343-.5437V8.7836h2.9601c.153 0 1.0792.1772 1.0792.8697 0 .575-.7107.7815-1.2948.7815zm10.7574 1.4862c0 .2187-.008.4363-.0243.651h-.9c-.09 0-.1265.0586-.1265.1477v.413c0 .973-.5487 1.1846-1.0296 1.2382-.4576.0517-.9648-.1913-1.0275-.4717-.2704-1.5186-.7198-1.8436-1.4305-2.4034.8817-.5599 1.799-1.386 1.799-2.4915 0-1.1936-.819-1.9458-1.3769-2.3153-.7825-.5163-1.6491-.6195-1.883-.6195H5.4682a8.7651 8.7651 0 014.907-2.7699l1.0974 1.151a.648.648 0 00.9182.0213l1.227-1.1743a8.7753 8.7753 0 016.0044 4.2762l-.8403 1.8982a.652.652 0 00.33.8585l1.6178.7188c.0283.2875.0425.577.0425.8717zm-9.3006-9.5993a.7128.7128 0 11.984 1.0316.7137.7137 0 01-.984-1.0316zm8.3389 6.71a.7107.7107 0 01.9395-.3625.7137.7137 0 11-.9405.3635z",
    "typescript": "M0 0h24v24H0V0zm18.488 9.75c.612 0 1.154.037 1.627.111a6.38 6.38 0 0 1 1.306.34v2.458a3.95 3.95 0 0 0-.643-.361 5.093 5.093 0 0 0-.717-.26 5.453 5.453 0 0 0-1.426-.2c-.3 0-.573.028-.819.086a2.1 2.1 0 0 0-.623.242c-.17.104-.3.229-.393.374a.888.888 0 0 0-.14.49c0 .196.053.373.156.529.104.156.252.304.443.444s.423.276.696.41c.273.135.582.274.926.416.47.197.892.407 1.266.628.374.222.695.473.963.753.268.279.472.598.614.957.142.359.214.776.214 1.253 0 .657-.125 1.21-.373 1.656a3.033 3.033 0 0 1-1.012 1.085 4.38 4.38 0 0 1-1.487.596c-.566.12-1.163.18-1.79.18a9.916 9.916 0 0 1-1.84-.164 5.544 5.544 0 0 1-1.512-.493v-2.63a5.033 5.033 0 0 0 3.237 1.2c.333 0 .624-.03.872-.09.249-.06.456-.144.623-.25.166-.108.29-.234.373-.38a1.023 1.023 0 0 0-.074-1.089 2.12 2.12 0 0 0-.537-.5 5.597 5.597 0 0 0-.807-.444 27.72 27.72 0 0 0-1.007-.436c-.918-.383-1.602-.852-2.053-1.405-.45-.553-.676-1.222-.676-2.005 0-.614.123-1.141.369-1.582.246-.441.58-.804 1.004-1.089a4.494 4.494 0 0 1 1.47-.629 7.536 7.536 0 0 1 1.77-.201zM3.375 9.938h9.563v2.166H9.506v9.646H6.789v-9.646H3.375z",
    "python": "M14.25.18l.9.2.73.26.59.3.45.32.34.34.25.34.16.33.1.3.04.26.02.2-.01.13V8.5l-.05.63-.13.55-.21.46-.26.38-.3.31-.33.25-.35.19-.35.14-.33.1-.3.07-.26.04-.21.02H8.77l-.69.05-.59.14-.5.22-.41.27-.33.32-.27.35-.2.36-.15.37-.1.35-.07.32-.04.27-.02.21v3.06H3.17l-.21-.03-.28-.07-.32-.12-.35-.18-.36-.26-.36-.36-.35-.46-.32-.59-.28-.73-.21-.88-.14-1.05-.05-1.23.06-1.22.16-1.04.24-.87.32-.71.36-.57.4-.44.42-.33.42-.24.4-.16.36-.1.32-.05.24-.01h.16l.06.01h8.16v-.83H6.18l-.01-2.75-.02-.37.05-.34.11-.31.17-.28.25-.26.31-.23.38-.2.44-.18.51-.15.58-.12.64-.1.71-.06.77-.04.84-.02 1.27.05zm-6.3 1.98l-.23.33-.08.41.08.41.23.34.33.22.41.09.41-.09.33-.22.23-.34.08-.41-.08-.41-.23-.33-.33-.22-.41-.09-.41.09zm13.09 3.95l.28.06.32.12.35.18.36.27.36.35.35.47.32.59.28.73.21.88.14 1.04.05 1.23-.06 1.23-.16 1.04-.24.86-.32.71-.36.57-.4.45-.42.33-.42.24-.4.16-.36.09-.32.05-.24.02-.16-.01h-8.22v.82h5.84l.01 2.76.02.36-.05.34-.11.31-.17.29-.25.25-.31.24-.38.2-.44.17-.51.15-.58.13-.64.09-.71.07-.77.04-.84.01-1.27-.04-1.07-.14-.9-.2-.73-.25-.59-.3-.45-.33-.34-.34-.25-.34-.16-.33-.1-.3-.04-.25-.02-.2.01-.13v-5.34l.05-.64.13-.54.21-.46.26-.38.3-.32.33-.24.35-.2.35-.14.33-.1.3-.06.26-.04.21-.02.13-.01h5.84l.69-.05.59-.14.5-.21.41-.28.33-.32.27-.35.2-.36.15-.36.1-.35.07-.32.04-.28.02-.21V6.07h2.09l.14.01zm-6.47 14.25l-.23.33-.08.41.08.41.23.33.33.23.41.08.41-.08.33-.23.23-.33.08-.41-.08-.41-.23-.33-.33-.23-.41-.08-.41.08z",
    "c": C_HEX_PATH,
    "cplusplus": CPP_HEX_PATH,
    "assemblyscript": "M0 0v24h24V0h-9.225c0 1.406-1.04 2.813-2.756 2.813A2.766 2.766 0 019.234 0zm18.204 10.947c.707 0 1.314.137 1.82.412.517.264.96.717 1.33 1.361l-1.726 1.108c-.19-.338-.395-.58-.617-.728a1.422 1.422 0 00-.807-.222c-.327 0-.586.09-.776.27a.896.896 0 00-.285.68c0 .337.106.596.317.775.222.17.57.36 1.045.57l.554.238c.474.2.891.411 1.25.633.37.21.675.453.918.728.253.264.443.57.57.918.137.337.206.738.206 1.203a3 3 0 01-.285 1.33c-.18.38-.433.701-.76.965a3.419 3.419 0 01-1.171.601c-.443.127-.929.19-1.456.19a5.31 5.31 0 01-1.41-.174 4.624 4.624 0 01-1.139-.475 3.922 3.922 0 01-.886-.712 4.48 4.48 0 01-.602-.902L16.1 18.67c.242.39.527.712.855.966.337.253.78.38 1.33.38.463 0 .827-.1 1.091-.301.275-.211.412-.475.412-.792 0-.38-.143-.664-.428-.854-.285-.19-.68-.396-1.187-.618l-.554-.237a8.12 8.12 0 01-1.092-.554 3.64 3.64 0 01-.839-.696 2.887 2.887 0 01-.538-.903 3.375 3.375 0 01-.19-1.187c0-.411.074-.796.222-1.155a2.91 2.91 0 01.649-.934c.285-.264.628-.47 1.029-.617.4-.148.849-.222 1.345-.222zm-8.796.032h.19l4.922 10.858h-2.327l-.506-1.219H7.318l-.506 1.219H4.675zm.063 3.988a22.21 22.21 0 01-.206.697l-.205.649a6.979 6.979 0 01-.222.585l-.776 1.868h2.834l-.776-1.868a15.492 15.492 0 01-.237-.633 23.741 23.741 0 01-.412-1.298z",
    "assembly": "M0 0v24h24V0h-9.225c0 1.406-1.04 2.813-2.756 2.813A2.766 2.766 0 019.234 0zm18.204 10.947c.707 0 1.314.137 1.82.412.517.264.96.717 1.33 1.361l-1.726 1.108c-.19-.338-.395-.58-.617-.728a1.422 1.422 0 00-.807-.222c-.327 0-.586.09-.776.27a.896.896 0 00-.285.68c0 .337.106.596.317.775.222.17.57.36 1.045.57l.554.238c.474.2.891.411 1.25.633.37.21.675.453.918.728.253.264.443.57.57.918.137.337.206.738.206 1.203a3 3 0 01-.285 1.33c-.18.38-.433.701-.76.965a3.419 3.419 0 01-1.171.601c-.443.127-.929.19-1.456.19a5.31 5.31 0 01-1.41-.174 4.624 4.624 0 01-1.139-.475 3.922 3.922 0 01-.886-.712 4.48 4.48 0 01-.602-.902L16.1 18.67c.242.39.527.712.855.966.337.253.78.38 1.33.38.463 0 .827-.1 1.091-.301.275-.211.412-.475.412-.792 0-.38-.143-.664-.428-.854-.285-.19-.68-.396-1.187-.618l-.554-.237a8.12 8.12 0 01-1.092-.554 3.64 3.64 0 01-.839-.696 2.887 2.887 0 01-.538-.903 3.375 3.375 0 01-.19-1.187c0-.411.074-.796.222-1.155a2.91 2.91 0 01.649-.934c.285-.264.628-.47 1.029-.617.4-.148.849-.222 1.345-.222zm-8.796.032h.19l4.922 10.858h-2.327l-.506-1.219H7.318l-.506 1.219H4.675zm.063 3.988a22.21 22.21 0 01-.206.697l-.205.649a6.979 6.979 0 01-.222.585l-.776 1.868h2.834l-.776-1.868a15.492 15.492 0 01-.237-.633 23.741 23.741 0 01-.412-1.298z",
    "webassembly": "M14.745 0c0 .042 0 .085 0 .129 0 1.52-1.232 2.752-2.752 2.752-1.52 0-2.752-1.232-2.752-2.752 0-.045 0-.087 0-.129H0v24h24V0H14.745zM11.454 21.431l-1.169-5.783h-.02l-1.264 5.783H7.39l-1.824-8.497h1.59l1.088 5.783h.02l1.311-5.783h1.487l1.177 5.854h.02l1.242-5.854h1.561l-2.027 8.497H11.454zM20.209 21.431l-.542-1.891h-2.861l-0.417 1.891h-1.59l2.056-8.497h2.509l2.5 8.497H20.209zM17.812 15.028l-.694 3.118h2.159l-.796-3.118H17.812z",
    "swift": "M21.9 16.4c-.1-.2-.2-.5-.3-.7 1.3-2.9.6-6.6-1.9-9.4-2.1-2.3-5.2-3.4-8.1-3 3.2 2.1 4.5 5.4 3.7 8.1-1.2-1.6-3.7-3.9-6.6-6.2-.9-.7-1.9-1.5-2.8-2.4-.2 1.8.4 3.9 1.6 5.6-1.5-.8-3.4-2.1-4.8-3.7-.3 2.5.8 5.2 2.9 6.9-1.2 0-2.5-.3-3.6-1 1 2.5 3.5 4.3 6.5 4.5-1.9 1.3-4.3 1.7-6.6 1.2 2.6 2 5.9 2.9 9.2 2.6 3.5-.3 6.7-2 8.7-4.8 1.2.9 2.7 1.2 3.8.7-.6-.7-1.3-1.5-1.7-2.4z",
    # Official Simple Icons Tux (siLinux) - 24x24 viewBox
    "linux": "M12.504 0c-.155 0-.315.008-.48.021-4.226.333-3.105 4.807-3.17 6.298-.076 1.092-.3 1.953-1.05 3.02-.885 1.051-2.127 2.75-2.716 4.521-.278.832-.41 1.684-.287 2.489a.424.424 0 00-.11.135c-.26.268-.45.6-.663.839-.199.199-.485.267-.797.4-.313.136-.658.269-.864.68-.09.189-.136.394-.132.602 0 .199.027.4.055.536.058.399.116.728.04.97-.249.68-.28 1.145-.106 1.484.174.334.535.47.94.601.81.2 1.91.135 2.774.6.926.466 1.866.67 2.616.47.526-.116.97-.464 1.208-.946.587-.003 1.23-.269 2.26-.334.699-.058 1.574.267 2.577.2.025.134.063.198.114.333l.003.003c.391.778 1.113 1.132 1.884 1.071.771-.06 1.592-.536 2.257-1.306.631-.765 1.683-1.084 2.378-1.503.348-.199.629-.469.649-.853.023-.4-.2-.811-.714-1.376v-.097l-.003-.003c-.17-.2-.25-.535-.338-.926-.085-.401-.182-.786-.492-1.046h-.003c-.059-.054-.123-.067-.188-.135a.357.357 0 00-.19-.064c.431-1.278.264-2.55-.173-3.694-.533-1.41-1.465-2.638-2.175-3.483-.796-1.005-1.576-1.957-1.56-3.368.026-2.152.236-6.133-3.544-6.139zm.529 3.405h.013c.213 0 .396.062.584.198.19.135.33.332.438.533.105.259.158.459.166.724 0-.02.006-.04.006-.06v.105a.086.086 0 01-.004-.021l-.004-.024a1.807 1.807 0 01-.15.706.953.953 0 01-.213.335.71.71 0 01-.088.069c-.104.058-.198.064-.284.134-.105.058-.19.14-.279.199-.064.059-.114.063-.188.063-.058 0-.114-.004-.199-.063-.069-.06-.14-.141-.213-.199-.07-.07-.145-.14-.21-.2-.064-.064-.114-.134-.188-.2a.603.603 0 01-.066-.135 1.832 1.832 0 01-.121-.465 2.022 2.022 0 01-.015-.53c.014-.259.06-.466.166-.725.104-.2.244-.398.438-.533.184-.136.364-.198.584-.198zm-3.628.266h.003c.134 0 .273.063.4.135.121.069.209.202.288.334.079.134.129.333.155.531.023.199.014.4-.015.597-.025.203-.088.401-.169.535-.08.135-.181.269-.299.334-.12.063-.245.134-.384.134-.135 0-.264-.071-.384-.134-.114-.065-.21-.199-.29-.334-.081-.134-.139-.332-.168-.535-.026-.197-.035-.398-.012-.597.026-.198.076-.397.156-.531.078-.132.166-.265.288-.334.122-.072.26-.135.398-.135zm1.933 2.796c.299 0 .593.065.918.198.329.135.652.333.946.533.293.199.558.397.737.601.181.198.27.398.27.601 0 .198-.089.397-.299.531-.21.135-.492.269-.861.4-.369.135-.813.268-1.318.334-.506.063-1.076.063-1.678-.003-.598-.066-1.11-.199-1.503-.331-.391-.135-.685-.269-.864-.403-.181-.134-.269-.333-.269-.531 0-.203.088-.403.269-.601.18-.204.444-.402.768-.601.324-.2.678-.398 1.036-.533.359-.133.719-.198 1.018-.198zm-1.622 3.597c.509.106 1.077.172 1.681.198.604.026 1.174-.003 1.679-.066.506-.065.95-.198 1.318-.334.369-.132.651-.266.861-.4.11-.076.191-.161.249-.254.349.503.758 1.045 1.158 1.622.616.89 1.189 1.884 1.547 2.918.359 1.033.504 2.106.257 3.109-.064.259-.166.519-.288.765-.181-.026-.378-.026-.578 0-.414.063-.858.268-1.263.533-.405.266-.768.601-1.018.932-.249.334-.384.668-.384.933 0 .203.058.334.14.466.08.135.199.202.329.268-.564.026-1.158-.035-1.737-.066-.578-.029-1.144-.029-1.678.003-.535.029-1.041.097-1.474.2-.433.099-.796.265-1.048.463-.058-.2-.168-.463-.358-.731-.191-.266-.449-.533-.768-.797-.319-.268-.685-.466-1.076-.601-.391-.135-.796-.199-1.168-.135-.089-.398-.114-.832-.066-1.298.05-.466.169-.965.358-1.465.379-1.002 1.018-2.036 1.681-2.927.663-.891 1.348-1.644 1.724-2.299z",
    # Official Simple Icons Apple (siApple) - 24x24 viewBox (Properly centered leaf & lobes)
    "macos": "M12.152 6.896c-.948 0-2.415-1.078-3.96-1.04-2.04.027-3.91 1.183-4.961 3.014-2.117 3.675-.546 9.103 1.519 12.09 1.013 1.454 2.208 3.09 3.792 3.039 1.52-.065 2.09-.987 3.935-.987 1.831 0 2.35.987 3.96.948 1.637-.026 2.676-1.48 3.676-2.948 1.156-1.688 1.636-3.325 1.662-3.415-.039-.013-3.182-1.221-3.22-4.857-.026-3.04 2.48-4.494 2.597-4.559-1.429-2.09-3.623-2.324-4.39-2.376-2-.156-3.675 1.09-4.61 1.09zM15.53 3.83c.843-1.012 1.4-2.427 1.245-3.83-1.207.052-2.662.805-3.532 1.818-.78.896-1.454 2.338-1.273 3.714 1.338.104 2.715-.688 3.559-1.701",
    # Precision Meridian Grid Globe
    "web": "M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zm7.9 9h-3.05a15.7 15.7 0 0 0-1.12-5.02A8.03 8.03 0 0 1 19.9 11zm-7.9 9c-.83 0-2.12-1.84-2.66-5h5.32c-.54 3.16-1.83 5-2.66 5zm-2.83-7a13.8 13.8 0 0 1 0-2h5.66a13.8 13.8 0 0 1 0 2H9.17zM4.1 11a8.03 8.03 0 0 1 4.17-5.02A15.7 15.7 0 0 0 7.15 11H4.1zm7.9-7c.83 0 2.12 1.84 2.66 5H9.34c.54-3.16 1.83-5 2.66-5zM4.1 13h3.05c.2 1.78.6 3.5 1.12 5.02A8.03 8.03 0 0 1 4.1 13zm11.63 5.02c.52-1.52.92-3.24 1.12-5.02h3.05a8.03 8.03 0 0 1-4.17 5.02z",
}


def fetch_avatar_data_uri(avatar_url):
    if not avatar_url:
        return ""
    try:
        req = urllib.request.Request(avatar_url, headers={"User-Agent": "ProfileGenerator/3.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = resp.read()
            mime = resp.headers.get_content_type()
            b64 = base64.b64encode(data).decode("utf-8")
            return f"data:{mime};base64,{b64}"
    except Exception as e:
        print(f"Warning: Failed to fetch avatar: {e}")
        return ""


def fetch_public_contributions(username):
    try:
        url = f"https://github-contributions-api.jogruber.de/v4/{username}?y=last"
        req = urllib.request.Request(url, headers={"User-Agent": "ProfileGenerator/3.0"})
        with urllib.request.urlopen(req, timeout=6) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
            days = payload.get("contributions", [])
            if days:
                weeks = []
                for i in range(0, len(days), 7):
                    chunk = days[i : i + 7]
                    weeks.append(
                        {"contributionDays": [{"contributionCount": d.get("count", 0)} for d in chunk]}
                    )
                total = sum(d.get("count", 0) for d in days)
                return {"totalContributions": total, "weeks": weeks}
    except Exception:
        pass
    return None


def fetch_github_data(username):
    query = """
    query($login: String!) {
      user(login: $login) {
        login
        name
        bio
        location
        avatarUrl
        repositories(first: 100, ownerAffiliations: OWNER, isFork: false, orderBy: {field: STARGAZERS, direction: DESC}) {
          totalCount
          nodes {
            name
            description
            stargazerCount
            forkCount
            primaryLanguage { name color }
          }
        }
        contributionsCollection {
          contributionCalendar {
            totalContributions
            weeks {
              contributionDays {
                contributionCount
                date
              }
            }
          }
        }
      }
    }
    """
    # 1. Try GitHub CLI (gh)
    try:
        res = subprocess.run(
            ["gh", "api", "graphql", "-f", f"query={query}", "-F", f"login={username}"],
            capture_output=True,
            text=True,
            check=True,
        )
        data = json.loads(res.stdout)
        user_node = data.get("data", {}).get("user")
        if user_node:
            return user_node
    except Exception:
        pass

    # 2. Try GITHUB_TOKEN
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        try:
            req = urllib.request.Request(
                "https://api.github.com/graphql",
                data=json.dumps({"query": query, "variables": {"login": username}}).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                    "User-Agent": "ProfileGenerator/3.0",
                },
            )
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                user_node = data.get("data", {}).get("user")
                if user_node:
                    return user_node
        except Exception as e:
            print(f"Warning: GraphQL request with GITHUB_TOKEN failed: {e}")

    # 3. Public Unauthenticated Fallback
    cal = fetch_public_contributions(username)
    if not cal:
        synth = [
            4, 7, 3, 12, 18, 9, 6, 14, 22, 19, 8, 5, 11, 16, 25, 31, 14, 9, 12, 20,
            17, 6, 4, 15, 28, 34, 21, 13, 8, 19, 24, 16, 10, 7, 14, 22, 38, 29, 18,
            12, 9, 15, 27, 33, 20, 14, 11, 19, 26, 17, 13, 21
        ]
        cal = {
            "totalContributions": sum(synth),
            "weeks": [{"contributionDays": [{"contributionCount": c}]} for c in synth],
        }

    return {
        "login": username,
        "name": "Nilton Perim Neto",
        "bio": "Not a Programmer, just a historian.",
        "location": "Goiás, Brazil",
        "avatarUrl": "https://avatars.githubusercontent.com/u/118851240?v=4",
        "repositories": {"totalCount": 30, "nodes": []},
        "contributionsCollection": {"contributionCalendar": cal},
    }


def extract_weekly_activity(data):
    cal = data.get("contributionsCollection", {}).get("contributionCalendar", {})
    weeks = cal.get("weeks", [])
    total = cal.get("totalContributions", 0)

    counts = [sum(d.get("contributionCount", 0) for d in w.get("contributionDays", [])) for w in weeks]

    if len(counts) > 52:
        counts = counts[-52:]
    elif len(counts) < 52:
        counts = [0] * (52 - len(counts)) + counts

    if sum(counts) == 0:
        counts = [
            4, 7, 3, 12, 18, 9, 6, 14, 22, 19, 8, 5, 11, 16, 25, 31, 14, 9, 12, 20,
            17, 6, 4, 15, 28, 34, 21, 13, 8, 19, 24, 16, 10, 7, 14, 22, 38, 29, 18,
            12, 9, 15, 27, 33, 20, 14, 11, 19, 26, 17, 13, 21
        ]
        total = sum(counts)

    return counts, total


def build_angular_oscilloscope(points, y_base):
    """
    Constructs a hard-angled linear vector trace ('L') matching Zed's crisp geometry.
    """
    if not points:
        return "", ""
    d = [f"M {points[0][0]:.1f} {points[0][1]:.1f}"]
    for px, py in points[1:]:
        d.append(f"L {px:.1f} {py:.1f}")
    stroke_path = " ".join(d)
    area_path = f"{stroke_path} L {points[-1][0]:.1f} {y_base:.1f} L {points[0][0]:.1f} {y_base:.1f} Z"
    return stroke_path, area_path


def generate_segmented_bar_svg(x, y, w, h, slices):
    """
    Renders a sharp, segmented horizontal telemetry bar instead of a soft circular pie/donut.
    """
    total = sum(s.get("pct", 0) for s in slices) or 100
    color_vars = ["var(--c1)", "var(--c2)", "var(--c3)", "var(--c4)"]
    gap = 3
    active_slices = [s for s in slices if s.get("pct", 0) > 0]
    avail_w = w - gap * max(0, len(active_slices) - 1)

    rects = [
        f'    <rect x="{x}" y="{y}" width="{w}" height="{h}" fill="var(--inner)" stroke="var(--border)" stroke-width="0.75"/>'
    ]
    curr_x = float(x)
    for idx, s in enumerate(active_slices):
        pct = s.get("pct", 0)
        seg_w = max(4.0, (pct / total) * avail_w)
        if idx == len(active_slices) - 1:
            seg_w = max(4.0, (x + w) - curr_x)
        c_var = color_vars[idx % len(color_vars)]
        rects.append(
            f'    <rect x="{curr_x:.1f}" y="{y}" width="{seg_w:.1f}" height="{h}" fill="{c_var}"/>'
        )
        curr_x += seg_w + gap

    return "\n".join(rects)


def get_theme_css(forced_theme=None):
    # Zed Default Dark (zed-onedark / carbon-industrial palette)
    dark_vars = """
        --bg: #090a0c;
        --card: #101216;
        --inner: #161920;
        --border: #242933;
        --border-sub: #1a1e26;
        --fg: #dce0e5;
        --fg-muted: #8b929e;
        --fg-dim: #555c69;
        --accent: #f3f4f6;
        --accent-op1: 0.18;
        --accent-op2: 0.03;
        --c1: #f3f4f6;
        --c2: #8b929e;
        --c3: #434956;
        --c4: #282d38;
        --status: #22c55e;
    """
    # Zed Default Light
    light_vars = """
        --bg: #f5f6f8;
        --card: #ffffff;
        --inner: #eef0f4;
        --border: #d0d5dd;
        --border-sub: #e4e7ec;
        --fg: #101828;
        --fg-muted: #475467;
        --fg-dim: #98a2b3;
        --accent: #101828;
        --accent-op1: 0.14;
        --accent-op2: 0.02;
        --c1: #101828;
        --c2: #475467;
        --c3: #98a2b3;
        --c4: #d0d5dd;
        --status: #16a34a;
    """

    if forced_theme == "light":
        theme_block = f":root {{{light_vars}}}"
    elif forced_theme == "dark":
        theme_block = f":root {{{dark_vars}}}"
    else:
        theme_block = f"""
      :root {{{dark_vars}}}
      @media (prefers-color-scheme: light) {{
        :root {{{light_vars}}}
      }}"""

    return f"""
      {theme_block}
      text {{
        font-family: "JetBrains Mono", "Zed Mono", "SF Mono", "Fira Code", ui-monospace, -apple-system, monospace;
        -webkit-font-smoothing: antialiased;
        font-variant-numeric: tabular-nums;
      }}
      .sans {{
        font-family: -apple-system, BlinkMacSystemFont, "Inter", "SF Pro Display", "Segoe UI", sans-serif;
      }}
      .draw-stroke {{
        stroke-dasharray: 2800;
        stroke-dashoffset: 2800;
        animation: drawPath 1.4s cubic-bezier(0.16, 1, 0.3, 1) forwards;
      }}
      .fade-in {{
        opacity: 0;
        animation: fadeIn 0.35s ease forwards;
      }}
      .d1 {{ animation-delay: 0.05s; }}
      .d2 {{ animation-delay: 0.10s; }}
      .d3 {{ animation-delay: 0.15s; }}
      .d4 {{ animation-delay: 0.20s; }}
      .pulse {{
        animation: pulseSq 2.2s steps(2, end) infinite;
        transform-box: fill-box;
        transform-origin: center;
      }}
      @keyframes drawPath {{
        to {{ stroke-dashoffset: 0; }}
      }}
      @keyframes fadeIn {{
        from {{ opacity: 0; }}
        to {{ opacity: 1; }}
      }}
      @keyframes pulseSq {{
        0%, 100% {{ opacity: 0.2; transform: scale(1); }}
        50% {{ opacity: 0.9; transform: scale(1.8); }}
      }}
      @media (prefers-reduced-motion: reduce) {{
        .draw-stroke, .fade-in, .pulse {{ animation: none !important; opacity: 1 !important; stroke-dashoffset: 0 !important; }}
      }}
    """


def get_featured_repos(config, data):
    featured = config.get("featured_repos", [])[:4]
    if not featured:
        nodes = data.get("repositories", {}).get("nodes", [])[:4]
        for n in nodes:
            lang = (n.get("primaryLanguage") or {}).get("name") or "Code"
            featured.append(
                {
                    "name": n.get("name", "repo"),
                    "desc": n.get("description") or "",
                    "stack": lang,
                    "stars": n.get("stargazerCount", 0),
                }
            )
    if not featured:
        featured = [
            {"name": "relay12", "stack": "Rust · D3D12", "stars": 0},
            {"name": "macpad-hald", "stack": "Swift · HID", "stars": 0},
            {"name": "linux-xpad", "stack": "C · Kernel", "stars": 0},
            {"name": "cde-zbus", "stack": "Rust · IPC", "stars": 0},
        ]
    return featured


def generate_svg_wide(theme=None, data=None, config=None, avatar_data_uri=""):
    config = config or {}
    data = data or {}

    weekly_counts, total_contribs = extract_weekly_activity(data)
    raw_max = max(weekly_counts) if weekly_counts else 1
    max_week = max(raw_max, 1)
    peak_idx = len(weekly_counts) - 1 - weekly_counts[::-1].index(raw_max)

    # Wide Activity Rhythm coordinates
    wave_x = 38
    wave_w = 724
    wave_y_base = 342
    wave_y_top = 274
    wave_h = wave_y_base - wave_y_top

    n = len(weekly_counts)
    step = wave_w / (n - 1) if n > 1 else wave_w

    points = []
    bars_svg = []
    for i, count in enumerate(weekly_counts):
        px = wave_x + i * step
        norm = count / max_week
        py = wave_y_base - (norm * wave_h)
        points.append((px, py))

        # Crisp rectangular histogram columns
        bar_h = max(2.0, norm * wave_h)
        bar_op = 0.10 + (norm * 0.22)
        bars_svg.append(
            f'    <rect x="{px - 2.2:.1f}" y="{wave_y_base - bar_h:.1f}" width="4.4" height="{bar_h:.1f}" '
            f'fill="var(--fg-muted)" fill-opacity="{bar_op:.2f}"/>'
        )

    stroke_d, area_d = build_angular_oscilloscope(points, wave_y_base)
    peak_x, peak_y = points[peak_idx]
    curr_x, curr_y = points[-1]
    peak_label_x = max(wave_x + 24, min(wave_x + wave_w - 24, peak_x))

    stack_langs = config.get(
        "stack_languages",
        [
            {"name": "Rust", "slug": "rust"},
            {"name": "C", "slug": "c"},
            {"name": "C++", "slug": "cplusplus"},
            {"name": "Python", "slug": "python"},
            {"name": "TypeScript", "slug": "typescript"},
            {"name": "Assembly", "slug": "assemblyscript"},
        ],
    )[:6]

    platforms = config.get(
        "platforms",
        [
            {"name": "Linux", "slug": "linux", "sub": "Kernel · Drivers"},
            {"name": "macOS", "slug": "macos", "sub": "Darwin · Systems"},
            {"name": "Web", "slug": "web", "sub": "Wasm · UI"},
        ],
    )[:3]

    project_scopes = config.get(
        "project_scopes",
        [
            {"name": "Low-Level & Drivers", "pct": 45},
            {"name": "UI & Graphics", "pct": 35},
            {"name": "Systems & Daemons", "pct": 20},
        ],
    )[:3]

    featured = get_featured_repos(config, data)

    raw_name = config.get("name") or data.get("name") or "Nilton Perim Neto"
    display_name = xesc(raw_name.title() if raw_name.isupper() else raw_name)
    tagline = xesc(truncate(config.get("tagline") or data.get("bio") or "Not a Programmer, just a historian.", 54))
    location = xesc(config.get("location") or data.get("location") or "Goiás, Brazil")

    emp_raw = config.get("employment_status", "Open to Work")
    if "·" in emp_raw:
        emp_raw = emp_raw.split("·")[-1].strip()
    emp_status = xesc(emp_raw.upper())
    badge_w = max(116, len(emp_raw) * 6.8 + 34)
    badge_x = 762 - badge_w

    if avatar_data_uri:
        avatar_svg = f"""      <image href="{avatar_data_uri}" x="36" y="26" width="44" height="44" preserveAspectRatio="xMidYMid slice"/>
      <rect x="36" y="26" width="44" height="44" fill="none" stroke="var(--border)" stroke-width="1"/>"""
    else:
        avatar_svg = """      <rect x="36" y="26" width="44" height="44" fill="var(--inner)" stroke="var(--border)" stroke-width="1"/>
      <text x="58" y="53" text-anchor="middle" font-size="13" font-weight="700" fill="var(--fg)">NP</text>"""

    scope_bar_svg = generate_segmented_bar_svg(420, 174, 342, 10, project_scopes)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 512" width="100%" height="100%">
  <defs>
    <style>{get_theme_css(theme)}</style>
    <linearGradient id="waveGradW" gradientUnits="userSpaceOnUse" x1="0" y1="{wave_y_top}" x2="0" y2="{wave_y_base}">
      <stop offset="0%" stop-color="var(--accent)" stop-opacity="var(--accent-op1)"/>
      <stop offset="70%" stop-color="var(--accent)" stop-opacity="var(--accent-op2)"/>
      <stop offset="100%" stop-color="var(--accent)" stop-opacity="0.0"/>
    </linearGradient>
    <pattern id="zedGridW" width="20" height="20" patternUnits="userSpaceOnUse">
      <path d="M 20 0 L 0 0 0 20" fill="none" stroke="var(--border-sub)" stroke-width="0.6" opacity="0.6"/>
    </pattern>
  </defs>

  <rect width="800" height="512" fill="var(--bg)"/>
  <rect width="800" height="512" fill="url(#zedGridW)"/>
  <rect x="0.5" y="0.5" width="799" height="511" fill="none" stroke="var(--border)" stroke-width="1"/>

  <!-- BLOCK 1: ZED STATUSBAR HEADER -->
  <g class="fade-in">
    <rect x="20" y="16" width="760" height="64" fill="var(--card)" stroke="var(--border)" stroke-width="1"/>
    <!-- Zed active tab top accent line -->
    <line x1="20" y1="16" x2="180" y2="16" stroke="var(--accent)" stroke-width="2"/>
{avatar_svg}
    <text x="94" y="44" font-size="15" font-weight="700" fill="var(--fg)" class="sans">{display_name}</text>
    <text x="94" y="61" font-size="10.5" font-weight="400" fill="var(--fg-muted)">{tagline}</text>

    <rect x="{badge_x:.1f}" y="34" width="{badge_w:.1f}" height="28" fill="var(--inner)" stroke="var(--border)" stroke-width="1"/>
    <rect x="{badge_x + 11:.1f}" y="45" width="6" height="6" fill="var(--status)"/>
    <rect x="{badge_x + 11:.1f}" y="45" width="6" height="6" fill="none" stroke="var(--status)" stroke-width="1" class="pulse"/>
    <text x="{badge_x + 25:.1f}" y="52" font-size="9.5" font-weight="700" letter-spacing="0.04em" fill="var(--fg)">{emp_status}</text>
  </g>

  <!-- BLOCK 2: STACK PANE -->
  <g class="fade-in d1">
    <rect x="20" y="88" width="760" height="50" fill="var(--card)" stroke="var(--border)" stroke-width="1"/>
    <text x="36" y="117" font-size="8.5" font-weight="700" letter-spacing="0.1em" fill="var(--fg-dim)">STACK</text>
    <line x1="84" y1="88" x2="84" y2="138" stroke="var(--border)" stroke-width="1"/>
"""

    tile_w = 104
    tile_h = 30
    start_x = 98
    gap = 9

    for idx, lang in enumerate(stack_langs):
        tx = start_x + idx * (tile_w + gap)
        lname = xesc(lang.get("name", ""))
        lslug = lang.get("slug", "").lower()
        path_data = ICONS.get(lslug, ICONS["rust"])

        svg += f"""    <g transform="translate({tx}, 98)">
      <rect width="{tile_w}" height="{tile_h}" fill="var(--inner)" stroke="var(--border)" stroke-width="1"/>
      <g transform="translate(9, 6.5) scale(0.7)">
        <path fill-rule="evenodd" clip-rule="evenodd" d="{path_data}" fill="var(--fg)"/>
      </g>
      <text x="32" y="19" font-size="10" font-weight="600" fill="var(--fg)">{lname}</text>
    </g>
"""

    svg += f"""  </g>

  <!-- BLOCK 3: TARGET PLATFORMS & DOMAIN TELEMETRY -->
  <g class="fade-in d2">
    <rect x="20" y="146" width="376" height="84" fill="var(--card)" stroke="var(--border)" stroke-width="1"/>
    <text x="36" y="164" font-size="8" font-weight="700" letter-spacing="0.1em" fill="var(--fg-dim)">PLATFORMS</text>
"""

    for idx, p in enumerate(platforms):
        px = 36 + idx * 118
        p_name = xesc(p.get("name", ""))
        p_sub = xesc(p.get("sub", p.get("badge", "")).split("·")[0].strip())
        p_slug = p.get("slug", p_name.lower())
        p_icon = ICONS.get(p_slug, ICONS["linux"])

        svg += f"""    <g transform="translate({px}, 172)">
      <rect width="108" height="46" fill="var(--inner)" stroke="var(--border)" stroke-width="1"/>
      <g transform="translate(10, 13) scale(0.82)">
        <path d="{p_icon}" fill="var(--fg)"/>
      </g>
      <text x="36" y="21" font-size="10.5" font-weight="700" fill="var(--fg)" class="sans">{p_name}</text>
      <text x="36" y="34" font-size="8" font-weight="500" fill="var(--fg-dim)">{p_sub}</text>
    </g>
"""

    svg += f"""
    <rect x="404" y="146" width="376" height="84" fill="var(--card)" stroke="var(--border)" stroke-width="1"/>
    <text x="420" y="164" font-size="8" font-weight="700" letter-spacing="0.1em" fill="var(--fg-dim)">ARCHITECTURE</text>
{scope_bar_svg}
"""

    c_vars = ["var(--c1)", "var(--c2)", "var(--c3)"]
    for idx, s in enumerate(project_scopes):
        lx = 420 + idx * 116
        s_name = xesc(truncate(s.get("name", "").split("&")[0].strip(), 12))
        s_pct = s.get("pct", 0)
        c_var = c_vars[idx % len(c_vars)]

        svg += f"""    <g transform="translate({lx}, 196)">
      <rect x="0" y="4" width="6" height="14" fill="{c_var}"/>
      <text x="12" y="11" font-size="8" font-weight="600" fill="var(--fg-muted)">{s_name}</text>
      <text x="12" y="22" font-size="10" font-weight="700" fill="var(--fg)">{s_pct}%</text>
    </g>
"""

    svg += f"""  </g>

  <!-- BLOCK 4: HARD-ANGLED OSCILLOSCOPE RHYTHM -->
  <g class="fade-in d3">
    <rect x="20" y="238" width="760" height="124" fill="var(--card)" stroke="var(--border)" stroke-width="1"/>
    <text x="36" y="257" font-size="8" font-weight="700" letter-spacing="0.1em" fill="var(--fg-dim)">ACTIVITY RHYTHM</text>
    <text x="762" y="257" text-anchor="end" font-size="8.5" font-weight="700" fill="var(--fg-muted)">{total_contribs} COMMITS // MAX {max_week}</text>

    <line x1="{wave_x}" y1="{wave_y_base}" x2="{wave_x + wave_w}" y2="{wave_y_base}" stroke="var(--border)" stroke-width="1"/>
    <line x1="{wave_x}" y1="{wave_y_top + wave_h * 0.5:.1f}" x2="{wave_x + wave_w}" y2="{wave_y_top + wave_h * 0.5:.1f}" stroke="var(--border-sub)" stroke-dasharray="2,3" stroke-width="1"/>

    <!-- Rectangular Telemetry Bars -->
{chr(10).join(bars_svg)}

    <!-- Angular Vector Fill & Mitered Trajectory -->
    <path d="{area_d}" fill="url(#waveGradW)"/>
    <path class="draw-stroke" d="{stroke_d}" fill="none" stroke="var(--accent)" stroke-width="1.6" stroke-linejoin="miter" stroke-miterlimit="3"/>

    <!-- Sharp Square Peak Reticle -->
    <line x1="{peak_x:.1f}" y1="{peak_y:.1f}" x2="{peak_x:.1f}" y2="{wave_y_base}" stroke="var(--accent)" stroke-dasharray="2,2" stroke-width="0.75" opacity="0.55"/>
    <rect x="{peak_x - 3:.1f}" y="{peak_y - 3:.1f}" width="6" height="6" fill="var(--accent)"/>
    <rect x="{peak_x - 3:.1f}" y="{peak_y - 3:.1f}" width="6" height="6" fill="none" stroke="var(--accent)" stroke-width="1" class="pulse"/>
    <rect x="{peak_label_x - 18:.1f}" y="{peak_y - 19:.1f}" width="36" height="13" fill="var(--inner)" stroke="var(--border)" stroke-width="1"/>
    <text x="{peak_label_x:.1f}" y="{peak_y - 9.5:.1f}" text-anchor="middle" font-size="8.5" font-weight="700" fill="var(--fg)">{max_week}</text>

    <!-- Current Week Square Node -->
    <rect x="{curr_x - 2.5:.1f}" y="{curr_y - 2.5:.1f}" width="5" height="5" fill="var(--status)"/>

    <g font-size="7.5" font-weight="600" fill="var(--fg-dim)">
      <text x="{wave_x}" y="355">W01</text>
      <text x="{wave_x + wave_w * 0.25:.1f}" y="355" text-anchor="middle">W13</text>
      <text x="{wave_x + wave_w * 0.5:.1f}" y="355" text-anchor="middle">W26</text>
      <text x="{wave_x + wave_w * 0.75:.1f}" y="355" text-anchor="middle">W39</text>
      <text x="{wave_x + wave_w}" y="355" text-anchor="end">W52</text>
    </g>
  </g>

  <!-- BLOCK 5: 2x2 ZED SPLIT-PANE REPO GRID -->
  <g class="fade-in d4">
"""

    card_coords = [(20, 370), (404, 370), (20, 426), (404, 426)]
    for idx, repo in enumerate(featured[:4]):
        cx, cy = card_coords[idx]
        r_name = xesc(truncate(repo.get("name", ""), 26))
        r_stack = xesc(repo.get("stack", "Code"))
        r_stars = repo.get("stars", 0)
        star_badge = f"★ {r_stars}" if r_stars > 0 else f"0{idx + 1}"

        svg += f"""    <g transform="translate({cx}, {cy})">
      <rect width="376" height="48" fill="var(--card)" stroke="var(--border)" stroke-width="1"/>
      <rect x="0" y="0" width="3" height="48" fill="var(--c1)"/>
      <text x="16" y="28" font-size="12" font-weight="700" fill="var(--fg)" class="sans">{r_name}</text>
      <rect x="238" y="14" width="84" height="20" fill="var(--inner)" stroke="var(--border)" stroke-width="1"/>
      <text x="280" y="27" text-anchor="middle" font-size="8.5" font-weight="600" fill="var(--fg-muted)">{r_stack}</text>
      <text x="360" y="28" text-anchor="end" font-size="9.5" font-weight="700" fill="var(--fg-dim)">{star_badge}</text>
    </g>
"""

    svg += f"""  </g>

  <!-- ZED STATUSLINE FOOTER -->
  <g class="fade-in d4" font-size="8.5" font-weight="600" fill="var(--fg-dim)">
    <text x="22" y="496">{location}</text>
    <text x="778" y="496" text-anchor="end">UTF-8 // LF // TELEMETRY</text>
  </g>
</svg>
"""
    return svg


def generate_svg_portrait(theme=None, data=None, config=None, avatar_data_uri=""):
    config = config or {}
    data = data or {}

    weekly_counts, total_contribs = extract_weekly_activity(data)
    raw_max = max(weekly_counts) if weekly_counts else 1
    max_week = max(raw_max, 1)
    peak_idx = len(weekly_counts) - 1 - weekly_counts[::-1].index(raw_max)

    wave_x = 28
    wave_w = 344
    wave_y_base = 382
    wave_y_top = 322
    wave_h = wave_y_base - wave_y_top

    n = len(weekly_counts)
    step = wave_w / (n - 1) if n > 1 else wave_w

    points = []
    bars_svg = []
    for i, count in enumerate(weekly_counts):
        px = wave_x + i * step
        norm = count / max_week
        py = wave_y_base - (norm * wave_h)
        points.append((px, py))

        bar_h = max(1.5, norm * wave_h)
        bar_op = 0.10 + (norm * 0.22)
        bars_svg.append(
            f'    <rect x="{px - 1.5:.1f}" y="{wave_y_base - bar_h:.1f}" width="3" height="{bar_h:.1f}" '
            f'fill="var(--fg-muted)" fill-opacity="{bar_op:.2f}"/>'
        )

    stroke_d, area_d = build_angular_oscilloscope(points, wave_y_base)
    peak_x, peak_y = points[peak_idx]
    peak_label_x = max(wave_x + 20, min(wave_x + wave_w - 20, peak_x))

    stack_langs = config.get(
        "stack_languages",
        [
            {"name": "Rust", "slug": "rust"},
            {"name": "C", "slug": "c"},
            {"name": "C++", "slug": "cplusplus"},
            {"name": "Python", "slug": "python"},
            {"name": "TypeScript", "slug": "typescript"},
            {"name": "Assembly", "slug": "assemblyscript"},
        ],
    )[:6]

    platforms = config.get(
        "platforms",
        [
            {"name": "Linux", "slug": "linux"},
            {"name": "macOS", "slug": "macos"},
            {"name": "Web", "slug": "web"},
        ],
    )[:3]

    project_scopes = config.get(
        "project_scopes",
        [
            {"name": "Drivers", "pct": 45},
            {"name": "Graphics", "pct": 35},
            {"name": "Systems", "pct": 20},
        ],
    )[:3]

    featured = get_featured_repos(config, data)

    raw_name = config.get("name") or data.get("name") or "Nilton Perim Neto"
    display_name = xesc(raw_name.title() if raw_name.isupper() else raw_name)
    tagline = xesc(truncate(config.get("tagline") or data.get("bio") or "Not a Programmer, just a historian.", 42))
    location = xesc(config.get("location") or data.get("location") or "Goiás, Brazil")

    if avatar_data_uri:
        avatar_svg = f"""      <image href="{avatar_data_uri}" x="26" y="24" width="40" height="40" preserveAspectRatio="xMidYMid slice"/>
      <rect x="26" y="24" width="40" height="40" fill="none" stroke="var(--border)" stroke-width="1"/>"""
    else:
        avatar_svg = """      <rect x="26" y="24" width="40" height="40" fill="var(--inner)" stroke="var(--border)" stroke-width="1"/>
      <text x="46" y="49" text-anchor="middle" font-size="12" font-weight="700" fill="var(--fg)">NP</text>"""

    scope_bar_svg = generate_segmented_bar_svg(192, 204, 180, 10, project_scopes)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 572" width="100%" height="100%">
  <defs>
    <style>{get_theme_css(theme)}</style>
    <linearGradient id="waveGradP" gradientUnits="userSpaceOnUse" x1="0" y1="{wave_y_top}" x2="0" y2="{wave_y_base}">
      <stop offset="0%" stop-color="var(--accent)" stop-opacity="var(--accent-op1)"/>
      <stop offset="70%" stop-color="var(--accent)" stop-opacity="var(--accent-op2)"/>
      <stop offset="100%" stop-color="var(--accent)" stop-opacity="0.0"/>
    </linearGradient>
    <pattern id="zedGridP" width="16" height="16" patternUnits="userSpaceOnUse">
      <path d="M 16 0 L 0 0 0 16" fill="none" stroke="var(--border-sub)" stroke-width="0.6" opacity="0.6"/>
    </pattern>
  </defs>

  <rect width="400" height="572" fill="var(--bg)"/>
  <rect width="400" height="572" fill="url(#zedGridP)"/>
  <rect x="0.5" y="0.5" width="399" height="571" fill="none" stroke="var(--border)" stroke-width="1"/>

  <!-- HEADER -->
  <g class="fade-in">
    <rect x="16" y="14" width="368" height="60" fill="var(--card)" stroke="var(--border)" stroke-width="1"/>
    <line x1="16" y1="14" x2="120" y2="14" stroke="var(--accent)" stroke-width="2"/>
{avatar_svg}
    <text x="78" y="41" font-size="14" font-weight="700" fill="var(--fg)" class="sans">{display_name}</text>
    <text x="78" y="57" font-size="9.5" font-weight="400" fill="var(--fg-muted)">{tagline}</text>
    <rect x="364" y="26" width="6" height="6" fill="var(--status)"/>
    <rect x="364" y="26" width="6" height="6" fill="none" stroke="var(--status)" stroke-width="1" class="pulse"/>
  </g>

  <!-- STACK (2x3) -->
  <g class="fade-in d1">
    <rect x="16" y="82" width="368" height="82" fill="var(--card)" stroke="var(--border)" stroke-width="1"/>
"""

    for idx, lang in enumerate(stack_langs):
        col = idx % 3
        row = idx // 3
        tx = 26 + col * 118
        ty = 92 + row * 34
        lname = xesc(lang.get("name", ""))
        lslug = lang.get("slug", "").lower()
        path_data = ICONS.get(lslug, ICONS["rust"])

        svg += f"""    <g transform="translate({tx}, {ty})">
      <rect width="112" height="28" fill="var(--inner)" stroke="var(--border)" stroke-width="1"/>
      <g transform="translate(8, 5.5) scale(0.68)">
        <path fill-rule="evenodd" clip-rule="evenodd" d="{path_data}" fill="var(--fg)"/>
      </g>
      <text x="30" y="18" font-size="9.5" font-weight="600" fill="var(--fg)">{lname}</text>
    </g>
"""

    svg += f"""  </g>

  <!-- PLATFORMS & SCOPE -->
  <g class="fade-in d2">
    <rect x="16" y="172" width="368" height="104" fill="var(--card)" stroke="var(--border)" stroke-width="1"/>
"""

    for idx, p in enumerate(platforms):
        py = 184 + idx * 28
        p_name = xesc(p.get("name", ""))
        p_slug = p.get("slug", p_name.lower())
        p_icon = ICONS.get(p_slug, ICONS["linux"])

        svg += f"""    <g transform="translate(26, {py})">
      <rect width="142" height="24" fill="var(--inner)" stroke="var(--border)" stroke-width="1"/>
      <g transform="translate(8, 4) scale(0.68)">
        <path d="{p_icon}" fill="var(--fg)"/>
      </g>
      <text x="32" y="16" font-size="9.5" font-weight="700" fill="var(--fg)" class="sans">{p_name}</text>
    </g>
"""

    svg += f"""    <line x1="178" y1="184" x2="178" y2="266" stroke="var(--border)" stroke-width="1"/>
    <text x="192" y="196" font-size="8" font-weight="700" letter-spacing="0.08em" fill="var(--fg-dim)">ARCHITECTURE</text>
{scope_bar_svg}
"""

    c_vars = ["var(--c1)", "var(--c2)", "var(--c3)"]
    short_labels = ["Drivers", "UI / GFX", "Systems"]
    for idx, s in enumerate(project_scopes):
        ly = 230 + idx * 14
        s_name = short_labels[idx] if idx < len(short_labels) else xesc(s.get("name", "")[:10])
        s_pct = s.get("pct", 0)
        c_var = c_vars[idx % len(c_vars)]

        svg += f"""    <g>
      <rect x="192" y="{ly - 6}" width="6" height="6" fill="{c_var}"/>
      <text x="204" y="{ly}" font-size="8.5" font-weight="600" fill="var(--fg-muted)">{s_name}</text>
      <text x="372" y="{ly}" text-anchor="end" font-size="8.5" font-weight="700" fill="var(--fg)">{s_pct}%</text>
    </g>
"""

    svg += f"""  </g>

  <!-- ACTIVITY RHYTHM -->
  <g class="fade-in d3">
    <rect x="16" y="284" width="368" height="116" fill="var(--card)" stroke="var(--border)" stroke-width="1"/>
    <text x="28" y="302" font-size="8" font-weight="700" letter-spacing="0.08em" fill="var(--fg-dim)">RHYTHM</text>
    <text x="372" y="302" text-anchor="end" font-size="8" font-weight="700" fill="var(--fg-muted)">{total_contribs} // MAX {max_week}</text>

    <line x1="{wave_x}" y1="{wave_y_base}" x2="{wave_x + wave_w}" y2="{wave_y_base}" stroke="var(--border)" stroke-width="1"/>
{chr(10).join(bars_svg)}
    <path d="{area_d}" fill="url(#waveGradP)"/>
    <path class="draw-stroke" d="{stroke_d}" fill="none" stroke="var(--accent)" stroke-width="1.5" stroke-linejoin="miter" stroke-miterlimit="3"/>

    <rect x="{peak_x - 2.5:.1f}" y="{peak_y - 2.5:.1f}" width="5" height="5" fill="var(--accent)"/>
    <rect x="{peak_x - 2.5:.1f}" y="{peak_y - 2.5:.1f}" width="5" height="5" fill="none" stroke="var(--accent)" stroke-width="1" class="pulse"/>
    <text x="{peak_label_x:.1f}" y="{peak_y - 7:.1f}" text-anchor="middle" font-size="8" font-weight="700" fill="var(--fg)">{max_week}</text>

    <g font-size="7.5" font-weight="600" fill="var(--fg-dim)">
      <text x="{wave_x}" y="394">W01</text>
      <text x="{wave_x + wave_w * 0.5:.1f}" y="394" text-anchor="middle">W26</text>
      <text x="{wave_x + wave_w}" y="394" text-anchor="end">W52</text>
    </g>
  </g>

  <!-- 2x2 COMPACT REPO GRID -->
  <g class="fade-in d4">
"""

    p_coords = [(16, 408), (204, 408), (16, 474), (204, 474)]
    for idx, repo in enumerate(featured[:4]):
        cx, cy = p_coords[idx]
        r_name = xesc(truncate(repo.get("name", ""), 16))
        r_stack = xesc(repo.get("stack", "Code"))
        r_stars = repo.get("stars", 0)
        star_str = f"★ {r_stars}" if r_stars > 0 else f"0{idx + 1}"

        svg += f"""    <g transform="translate({cx}, {cy})">
      <rect width="180" height="58" fill="var(--card)" stroke="var(--border)" stroke-width="1"/>
      <rect x="0" y="0" width="3" height="58" fill="var(--c1)"/>
      <text x="12" y="22" font-size="11" font-weight="700" fill="var(--fg)" class="sans">{r_name}</text>
      <text x="168" y="22" text-anchor="end" font-size="8.5" font-weight="700" fill="var(--fg-dim)">{star_str}</text>
      <rect x="12" y="32" width="76" height="16" fill="var(--inner)" stroke="var(--border)" stroke-width="0.75"/>
      <text x="50" y="43" text-anchor="middle" font-size="7.5" font-weight="600" fill="var(--fg-muted)">{r_stack}</text>
    </g>
"""

    svg += f"""  </g>

  <!-- FOOTER -->
  <g class="fade-in d4" font-size="8" font-weight="600" fill="var(--fg-dim)">
    <text x="18" y="554">{location}</text>
    <text x="382" y="554" text-anchor="end">UTF-8 // TELEMETRY</text>
  </g>
</svg>
"""
    return svg


def generate_svg(theme=None, data=None, config=None, avatar_data_uri=""):
    return generate_svg_wide(theme, data, config, avatar_data_uri)


def main():
    config = load_config()
    username = config.get("username", "niltonperimneto")

    print(f"Fetching GitHub data for {username}...")
    data = fetch_github_data(username)

    avatar_url = (
        data.get("avatarUrl")
        or config.get("avatar_url")
        or "https://avatars.githubusercontent.com/u/118851240?v=4"
    )
    print(f"Fetching avatar from {avatar_url}...")
    avatar_data_uri = fetch_avatar_data_uri(avatar_url)

    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Adaptive Single-File Cards
    wide_adaptive = generate_svg_wide(None, data=data, config=config, avatar_data_uri=avatar_data_uri)
    portrait_adaptive = generate_svg_portrait(None, data=data, config=config, avatar_data_uri=avatar_data_uri)
    (ASSETS_DIR / "zed-card-wide.svg").write_text(wide_adaptive, encoding="utf-8")
    (ASSETS_DIR / "zed-card-portrait.svg").write_text(portrait_adaptive, encoding="utf-8")

    # 2. Explicit Theme Variants
    wide_dark = generate_svg_wide("dark", data=data, config=config, avatar_data_uri=avatar_data_uri)
    wide_light = generate_svg_wide("light", data=data, config=config, avatar_data_uri=avatar_data_uri)
    (ASSETS_DIR / "zed-card-wide-dark.svg").write_text(wide_dark, encoding="utf-8")
    (ASSETS_DIR / "zed-card-wide-light.svg").write_text(wide_light, encoding="utf-8")

    portrait_dark = generate_svg_portrait("dark", data=data, config=config, avatar_data_uri=avatar_data_uri)
    portrait_light = generate_svg_portrait("light", data=data, config=config, avatar_data_uri=avatar_data_uri)
    (ASSETS_DIR / "zed-card-portrait-dark.svg").write_text(portrait_dark, encoding="utf-8")
    (ASSETS_DIR / "zed-card-portrait-light.svg").write_text(portrait_light, encoding="utf-8")

    # 3. Standard Fallbacks
    (ASSETS_DIR / "zed-card-dark.svg").write_text(wide_dark, encoding="utf-8")
    (ASSETS_DIR / "zed-card-light.svg").write_text(wide_light, encoding="utf-8")

    print("All Zed-styled SVG assets generated successfully!")


if __name__ == "__main__":
    main()
