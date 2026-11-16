"""Simplified Chinese, Traditional Chinese and English interface text."""
import ctypes
from ctypes import wintypes
import locale
import os
import sys


ZH = {
    'Show / hide pet': '显示／隐藏宠物',
    'Hide pet': '隐藏宠物',
    'Pet model': '宠物模型',
    'Import model…': '导入模型…',
    'Export model template…': '导出模型模板…',
    'Import colors…': '导入花色…',
    'Settings…': '设置…',
    'Pause typing': '暂停打字互动',
    'Feed a little hay': '喂一点草',
    'Quit WheekKeys': '退出 WheekKeys',
    'Potato': '土豆',
    'WheekKeys settings': 'WheekKeys 设置',
    'Key presses per meal': '吃草所需按键次数',
    'Movement speed (×)': '移动速度（倍）',
    'Display size (×)': '显示大小（倍）',
    'Keep pet above other windows': '始终显示在其他窗口上方',
    'Pause typing interaction': '暂停打字互动',
    'Changes take effect when you save.': '点击保存后生效，下次启动也会保留。',
    'Cancel': '取消',
    'Save': '保存',
    'Check your settings': '请检查设置',
    'Enter a whole number for keys per meal and numbers for speed and size.': '按键次数请填写整数，移动速度和显示大小请填写数字。',
    'Keys per meal must be an integer between 1 and 1000.': '吃草所需按键次数必须是 1～1000 之间的整数。',
    'Speed must be between 0.5 and 2.0.': '移动速度必须在 0.5～2 倍之间。',
    'Scale must be between 0.5 and 2.0.': '显示大小必须在 0.5～2 倍之间。',
    'Invalid switch value.': '开关设置无效。',
    'Invalid model or skin path.': '模型或花色文件路径无效。',
    'Invalid window position.': '窗口位置无效。',
    'Choose a model folder containing model.json': '选择包含 model.json 的模型文件夹',
    'Choose where to save the model template': '选择模型模板的保存位置',
    'Choose a palette': '选择花色文件',
    'Palette JSON': '花色文件（JSON）',
    'Cannot import model': '无法导入模型',
    'Cannot export template': '无法导出模型模板',
    'Cannot import colors': '无法导入花色',
    'Model template saved': '模型模板已保存',
    'Could not save settings': '无法保存设置',
    'Skipped invalid model: {error}': '已跳过无效的模型：{error}',
    'Could not load saved settings. Using defaults.\n{error}': '无法读取已保存的设置，将使用默认设置。\n{error}',
    'The saved model is unavailable. Using Potato.': '找不到上次使用的模型，已切换为土豆。',
    'Could not load colors. Using model colors.\n{error}': '无法读取花色文件，将使用模型自带的花色。\n{error}',
    'Tray icon could not start. The pet right-click menu is still available.\n{error}': '无法显示托盘图标，仍可使用宠物的右键菜单。\n{error}',
    'WheekKeys could not start': 'WheekKeys 无法启动',
    'Keyboard interaction stopped.\n{error}': '键盘互动已停止。\n{error}',
    'Type to grow hay for your guinea pig.': '敲键盘长牧草，豚鼠跑来吃。',
    'Palette JSON override for this session': '指定本次运行使用的花色 JSON 文件',
    'Automatic ten-second loop; no global keyboard input': '自动播放十秒循环演示，不读取全局按键',
    'Global keyboard mode requires Windows. Use --demo for an animation preview.': '全局按键互动需要 Windows。可使用 --demo 预览动画。',
    'Model name is required.': '请填写模型名称。',
    'All model files must be inside the model folder.': '模型文件必须位于模型文件夹内。',
    'Sprite sheets must be PNG, four equal columns, at most 8192×4096.': '动作图必须是 PNG 格式，分成四个等宽区域，且不超过 8192×4096 像素。',
    'Empty guinea pig sprite': '动作图中有空白帧。',
}


ZH_HANT = {'Show / hide pet': '顯示／隱藏寵物',
 'Hide pet': '隱藏寵物',
 'Pet model': '寵物模型',
 'Import model…': '匯入模型…',
 'Export model template…': '匯出模型範本…',
 'Import colors…': '匯入花色…',
 'Settings…': '設定…',
 'Pause typing': '暫停打字互動',
 'Feed a little hay': '餵一點草',
 'Quit WheekKeys': '結束 WheekKeys',
 'Potato': '土豆',
 'WheekKeys settings': 'WheekKeys 設定',
 'Key presses per meal': '吃草所需按鍵次數',
 'Movement speed (×)': '移動速度（倍）',
 'Display size (×)': '顯示大小（倍）',
 'Keep pet above other windows': '一律顯示在其他視窗上方',
 'Pause typing interaction': '暫停打字互動',
 'Changes take effect when you save.': '按下儲存後生效，下次啟動也會保留。',
 'Cancel': '取消',
 'Save': '儲存',
 'Check your settings': '請檢查設定',
 'Enter a whole number for keys per meal and numbers for speed and size.': '按鍵次數請填寫整數，移動速度和顯示大小請填寫數字。',
 'Keys per meal must be an integer between 1 and 1000.': '吃草所需按鍵次數必須是 1～1000 之間的整數。',
 'Speed must be between 0.5 and 2.0.': '移動速度必須在 0.5～2 倍之間。',
 'Scale must be between 0.5 and 2.0.': '顯示大小必須在 0.5～2 倍之間。',
 'Invalid switch value.': '開關設定無效。',
 'Invalid model or skin path.': '模型或花色檔案路徑無效。',
 'Invalid window position.': '視窗位置無效。',
 'Choose a model folder containing model.json': '選擇包含 model.json 的模型資料夾',
 'Choose where to save the model template': '選擇模型範本的儲存位置',
 'Choose a palette': '選擇花色檔案',
 'Palette JSON': '花色檔案（JSON）',
 'Cannot import model': '無法匯入模型',
 'Cannot export template': '無法匯出模型範本',
 'Cannot import colors': '無法匯入花色',
 'Model template saved': '模型範本已儲存',
 'Could not save settings': '無法儲存設定',
 'Skipped invalid model: {error}': '已略過無效的模型：{error}',
 'Could not load saved settings. Using defaults.\n{error}': '無法讀取已儲存的設定，將使用預設值。\n{error}',
 'The saved model is unavailable. Using Potato.': '找不到上次使用的模型，已切換為土豆。',
 'Could not load colors. Using model colors.\n{error}': '無法讀取花色檔案，將使用模型自帶的花色。\n{error}',
 'Tray icon could not start. The pet right-click menu is still available.\n{error}': '無法顯示系統匣圖示，仍可使用寵物的右鍵選單。\n'
                                                                                     '{error}',
 'WheekKeys could not start': 'WheekKeys 無法啟動',
 'Keyboard interaction stopped.\n{error}': '鍵盤互動已停止。\n{error}',
 'Type to grow hay for your guinea pig.': '敲鍵盤長牧草，天竺鼠跑來吃。',
 'Palette JSON override for this session': '指定本次執行使用的花色 JSON 檔案',
 'Automatic ten-second loop; no global keyboard input': '自動播放十秒循環示範，不讀取全域按鍵',
 'Global keyboard mode requires Windows. Use --demo for an animation preview.': '全域按鍵互動需要 Windows。可使用 --demo '
                                                                                '預覽動畫。',
 'Model name is required.': '請填寫模型名稱。',
 'All model files must be inside the model folder.': '模型檔案必須位於模型資料夾內。',
 'Sprite sheets must be PNG, four equal columns, at most 8192×4096.': '動作圖必須是 PNG 格式，分成四個等寬區域，且不超過 8192×4096 '
                                                                      '像素。',
 'Empty guinea pig sprite': '動作圖中有空白影格。'}
ZH.update({'Palette must be a JSON object.': '花色文件必须是 JSON 对象。',
           'Model manifest must be a JSON object.': '模型配置必须是 JSON 对象。',
           'Model file paths must be nonempty strings.': '模型文件路径必须是非空字符串。'})
ZH_HANT.update({'Palette must be a JSON object.': '花色檔案必須是 JSON 物件。',
                'Model manifest must be a JSON object.': '模型設定必須是 JSON 物件。',
                'Model file paths must be nonempty strings.': '模型檔案路徑必須是非空字串。'})
ZH.update({'Mochi': '奶糖'})
ZH_HANT.update({'Mochi': '奶糖'})
ZH.update({'Language': '语言', 'Follow system': '跟随系统', 'Invalid language.': '语言设置无效。'})
ZH_HANT.update({'Language': '語言', 'Follow system': '跟隨系統', 'Invalid language.': '語言設定無效。'})
LANGUAGES = ('auto', 'zh-Hans', 'zh-Hant', 'en')
LANGUAGE_NAMES = {'zh-Hans': '简体中文', 'zh-Hant': '繁體中文', 'en': 'English'}


def windows_ui_language():
    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
    get_language = kernel32.GetUserDefaultUILanguage
    get_language.argtypes = []
    get_language.restype = wintypes.WORD
    language = get_language()
    if not language:
        raise OSError('Windows did not return a UI language')
    # PRIMARYLANGID: all Chinese sublanguages, including CN, TW, HK and SG.
    if language & 0x3ff != 0x04:
        return 'en'
    return 'zh-Hant' if language >> 10 in (1, 3, 5, 31) else 'zh-Hans'


def detect_language():
    if sys.platform == 'win32':
        try:
            return windows_ui_language()
        except (OSError, AttributeError):
            pass
    name = next((os.environ[key] for key in ('LC_ALL', 'LC_MESSAGES', 'LANGUAGE', 'LANG')
                 if os.environ.get(key)), None)
    if name is None:
        try:
            name = locale.getlocale()[0] or ''
        except (ValueError, OSError):
            name = ''
    name = name.split(':', 1)[0].split('.', 1)[0].replace('-', '_').lower()
    parts = name.split('_')
    if parts[0] != 'zh':
        return 'en'
    if 'hant' in parts:
        return 'zh-Hant'
    if 'hans' in parts:
        return 'zh-Hans'
    return 'zh-Hant' if any(region in parts for region in ('tw', 'hk', 'mo')) else 'zh-Hans'


class Translator:
    def __init__(self, language=None):
        self.language = 'zh-Hans' if language == 'zh' else language if language in LANGUAGE_NAMES else detect_language()

    def __call__(self, text, **values):
        table = ZH_HANT if self.language == 'zh-Hant' else ZH if self.language == 'zh-Hans' else {}
        message = table.get(text, text)
        return message.format(**values) if values else message

    def model_name(self, model):
        names = {'potato': 'Potato', 'mochi': 'Mochi'}
        return self(names[model.id]) if model.id in names else model.name
