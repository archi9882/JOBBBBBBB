# 10/02　Okada 錯動：從斷層到初始水面

- 閱讀：[流體力學與 CFD 從零開始](https://claude.ai/artifact/UNkoMqkLDbPB72QRsM4TQf) 第 16 章 16-02（推導、可在瀏覽器執行的程式、實測輸出）
- 什麼時候做：卡 03（震央星號）之後。儲備課程，不排進每天的卡片進度。
- 分級：B（見 `docs/depth-tiers.md`）

## 問題
COMCOT 怎麼把斷層參數變成初始水面？「震央」是斷層面上的哪一點？

## 數學／原理
Okada (1985) 半無限彈性體解、Chinnery 記號；COMCOT Faulting Option 0＝斷層面中心、9＝上緣中點。

## 測試：通過條件
破裂到地表的斷層，破裂線兩側落差＝U sinδ（誤差 < 1e-3）；與 COMCOT 的 deform_seg001.dat 比較 RMS < 1 cm。

## 出貨條件
與其他儲備課程相同：`math.md`、`code/`、`tests/`、`falsification.md` 四項齊全且測試通過。網頁上的程式是參考答案；A 級課請先自己寫，卡住再看。
