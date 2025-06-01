import uiautomator2 as u2
import random
import time

d = u2.connect('127.0.0.1:62001')
pack = d.info['currentPackageName']
#sess = d.session(pack, attach=True)
crashList = []
height = d.info['displayHeight']
width = d.info['displayWidth']
mainAct = d.app_info(pack)['mainActivity']
fText = 'abc'
timeout = 60 * 5
waitTime = 0.6
rTime = 10  # response time of widget
frequencyCap = 4
visitMap = {}
stateList = []

class State:
    def __init__(self, image, act):
        self.image = image
        self.act = act
        self.event_list = []

class Event:
    def __init__(self, w_id, text, w_type, desc, w_img, e_type):
        self.w_id = w_id
        self.text = text
        self.w_type = w_type
        self.desc = desc
        self.w_img = w_img
        self.e_type = e_type
def isCrash():
    crash_cmd = "logcat -d AndroidRuntime:E CrashAnrDetector:D ActivityManager:E SQLiteDatabase:E WindowManager:E ActivityThread:E Parcel:E *:F *:S"
    out = d.shell(crash_cmd).output
    if out.__contains__("--------- beginning of crash"):
        crashList.append(out)
        return True
    return False
    #return not sess.alive

def crash():
    crash_cmd = "logcat -d AndroidRuntime:E CrashAnrDetector:D ActivityManager:E SQLiteDatabase:E WindowManager:E ActivityThread:E Parcel:E *:F *:S"
    out = d.shell(crash_cmd).output
    if out.__contains__("--------- beginning of crash"):
        return True
    return False

def getCurrentAct():
    return d.app_current()['activity']


def isDialog():
    isDialog = False
    enabledView = d(enabled='true')[0]
    visBounds = enabledView.info['visibleBounds']
    curWidth = visBounds['right'] - visBounds['left']
    curHeight = visBounds['bottom'] - visBounds['top']
    if (width / 8 <= curWidth <= width / 4 * 3) or (height / 8 <= curHeight <= height / 4 * 3):
        isDialog = True
    return isDialog


def isMenu():
    isMenu = False
    enabledView = d(enabled='true')[0]
    visBounds = enabledView.info['visibleBounds']
    curWidth = visBounds['right'] - visBounds['left']
    curHeight = visBounds['bottom'] - visBounds['top']
    #isOriSize = not ((curHeight == height) and (curWidth == width))
    isOriSize = (curHeight <= 0.95 * height) and (curWidth <= 0.95 * width)
    hasListView = d(className='android.widget.ListView').exists
    hasRecyclerView = d(className='android.support.v7.widget.RecyclerView').exists
    hasList = hasListView or hasRecyclerView
    if isOriSize and hasList:
        isMenu = True
    return isMenu


def gotoAnotherApp():
    curPackage = d.app_current()['package']
    return curPackage != pack


def restartApp():
    d.app_stop(pack)
    d.app_start(pack,wait=True)


def back():
    backBefore = d.screenshot(format='opencv')
    d.press('back')
    sim = d.image.match(backBefore)['similarity']
    if sim >= 0.99:
        d.press('back')
    time.sleep(waitTime)

def executeEvent(element, event):
    type = element.info['className']
    if type == 'android.widget.EditText':
        element.set_text(fText)
    else:
        d.implicitly_wait(rTime)
        if event == 'click' or event == 'item_click':
            element.click()
        elif event == 'long_click' or event == 'item_long_click':
            element.long_click()
    time.sleep(waitTime)

def isEditText(element):
    type = element.info['className']
    return type == 'android.widget.EditText'

def findRandomElement(elements):
    e_index = random.randint(0, len(elements)-1)
    return elements[e_index]

# def findOptimalElement(elements):
#     optElement = None
#     optInfo = None
#     next = 0
#     for i in range(len(elements)):
#         element = elements[i]
#         vInfo = visitMap[str(element.info)]
#         if vInfo['openType'] == 0:
#             optInfo = vInfo
#             optElement = element
#             next = i + 1
#             break
#     j = next
#     while j < len(elements):
#         element_j = elements[j]
#         vInfo_j = visitMap[str(element_j.info)]
#         if vInfo_j['opentype'] == 0 and vInfo_j['frequency'] < optInfo['frequency']:
#             optInfo = vInfo_j
#             optElement = element_j
#         j = j + 1
#     return optElement

# def getIndex(elements,e):
#     for i in range(len(elements)):
#         if e == elements[i]:
#             return i

def otherEvent():
    scroll = d(scrollable='true', instance=0)
    if scroll.exists:
        r = random.random()
        if r > 0.7:
            d.swipe_ext("down")
            longClickList = d(longClickable='true')
            if longClickList.exists:
                p_lc = random.random()
                if p_lc > 0.7:
                    lc_index = random.randint(0, len(longClickList)-1)
                    executeEvent(longClickList[lc_index],'long_click')
                else:
                    back()
            else:
                back()
        else:
            longClickList = d(longClickable='true')
            if longClickList.exists:
                p_lc = random.random()
                if p_lc > 0.7:
                    lc_index = random.randint(0, len(longClickList) - 1)
                    executeEvent(longClickList[lc_index], 'long_click')
                else:
                    back()
            else:
                back()

def explore():
    d.shell("logcat -c")
    startTime = time.time()
    endTime = startTime
    while endTime - startTime <= timeout:
        elements = d(clickable='true')
        if elements.exists:
            if not bool(visitMap):
                fir_element = elements[0]
                fir_dic = fir_element.info
                firAct = getCurrentAct()
                fir_dic['hostAct'] = firAct
                fir_info = str(fir_dic)
                executeEvent(fir_element,'click')
                firVisit = {'openType': 0, 'visit': True, 'frequency': 0}
                if isDialog() and (not crash()):
                    firVisit['openType'] = 1
                    firVisit['visit'] = False
                elif isMenu() and (not crash()):
                    firVisit['openType'] = 2
                    firVisit['visit'] = False
                nextFrequency = firVisit['frequency'] + 1;
                firVisit['frequency'] = nextFrequency
                visitMap[fir_info] = firVisit
            else:
                if gotoAnotherApp():
                    back()
                    curPack = d.app_current()['package']
                    if curPack == pack:
                        continue
                    else:
                        restartApp()
                        continue
                cele_index = 0
                for cele in elements:
                    hostAct = getCurrentAct()
                    isEdit = isEditText(cele)
                    cele_dic = cele.info
                    cele_dic['hostAct'] = hostAct
                    cele_info = str(cele_dic)
                    if(not cele_info in visitMap.keys()):
                        executeEvent(cele, 'click')
                        subVisit = {'openType':0,'visit':True,'frequency':0}
                        if isDialog() and (not isEdit) and (not crash()):
                            subVisit['openType'] = 1
                            subVisit['visit'] = False
                        elif isMenu() and (not isEdit) and (not crash()):
                            subVisit['openType'] = 2
                            subVisit['visit'] = False
                        nextFrequency = subVisit['frequency'] + 1
                        subVisit['frequency'] = nextFrequency
                        visitMap[cele_info] = subVisit
                        break
                    else:
                        dmVisit = visitMap[cele_info]
                        if not dmVisit['visit']:
                            executeEvent(cele, 'click')
                            dmFlag = True
                            dmElements = d(clickable='true')
                            for dmEle in dmElements:
                                dmEle_dic = dmEle.info
                                dmHostAct = getCurrentAct()
                                dmEle_dic['hostAct'] = dmHostAct
                                dmEle_info = str(dmEle_dic)
                                if(not dmEle_info in visitMap.keys()):
                                    dmFlag = False
                                    break
                                else:
                                    dmFlag = dmFlag and visitMap[dmEle_info]['visit']
                            nextFrequency = dmVisit['frequency'] + 1
                            dmVisit['frequency'] = nextFrequency
                            dmVisit['visit'] = dmFlag
                            if dmVisit['frequency'] > frequencyCap:
                                dmVisit['visit'] = True
                            break
                    if cele_index == len(elements) - 1:
                        curAct = getCurrentAct()
                        if ((pack + curAct) == mainAct) and (not isDialog()) and (not isMenu()):
                            lc_elements = d(longClickable = 'true')
                            if lc_elements.exists:
                                p_lc = random.random()
                                if p_lc >= 0.5:
                                    lc_index = random.randint(0, len(lc_elements)-1)
                                    executeEvent(lc_elements[lc_index], 'long_click')
                                    break
                                else:
                                    optElement = findRandomElement(elements)
                                    opt_hostAct = curAct
                                    opt_dic = optElement.info
                                    opt_dic['hostAct'] = opt_hostAct
                                    opt_str = str(opt_dic)
                                    opt_info = visitMap[opt_str]
                                    executeEvent(optElement, 'click')
                                    opt_info['frequency'] = opt_info['frequency'] + 1
                                    break
                            else:
                                optElement = findRandomElement(elements)
                                opt_hostAct = curAct
                                opt_dic = optElement.info
                                opt_dic['hostAct'] = opt_hostAct
                                opt_str = str(opt_dic)
                                opt_info = visitMap[opt_str]
                                executeEvent(optElement, 'click')
                                opt_info['frequency'] = opt_info['frequency'] + 1
                                # visitMap[opt_str] = opt_info
                                break
                        else:
                            #otherEvent()
                            back()
                            break
                    cele_index = cele_index + 1
        else:
            otherEvent()
            #back()
        if isCrash():
            d.shell("logcat -c")
            restartApp()
        endTime = time.time()


if __name__ == "__main__":
    explore()
    print(len(crashList))