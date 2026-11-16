# 改進想法（一行一條，週末再決定）

- 波動 × PINN 起點專案（1D 淺水 PINN vs 跳蛙、Carrier–Greenspan 溯上、KdV 守恆漂移、COMCOT→FNO 代理、潮位站反求參數），詳見文件 https://claude.ai/artifact/7qGgMBqj12YZEuBy8pA3ww
- 水文學 × PINN 的學術與業界進展（淹水河川、地下水、降雨逕流、綜述），詳見文件 https://claude.ai/artifact/PWN3Ypfwan2grTxCNYdPgs
- 新卡候選：在卡 41 的 SpectralConv1d 上加 PDE 殘差損失變成 PINO，測卡 42 的範圍外誤差 33% 會不會改善（Keppler 等 WRR 62(8) e2025WR042156, 2026 說純資料損失泛化差、加 PDE 損失才外插得動）
- 卡 40 的預測欄可加一問：測站只給 η 卻要反求 h，會不會失效？對照 Radfar（arXiv 2606.18149）只給水深 95.7%、只給流速 61.9%、兩者一起給 14.5% 的掃描結果
- wave1d_ref.py 加摩擦項（Manning n）才能做河川水力的反求題；現在的參考解是無摩擦線性淺水方程
