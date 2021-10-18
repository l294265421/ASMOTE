import matplotlib.pyplot as plt
from pylab import mpl

from nlp_tasks.absa.conf import data_path
from nlp_tasks.absa.utils import file_utils

plt.xticks(rotation=270)
mpl.rcParams['font.sans-serif'] = ['FangSong']

# file_path = data_path.data_base_dir + data_path.for_sentiment_visualization
# lines = file_utils.read_all_lines(file_path)

# attention = lines[0].strip('[[').strip(']]').split()
# attention = [float(e) for e in attention]
# words = lines[1].strip('\'').split()

# attention = [0.08, 0.08, 0.07, 0.2, 0.01, 0.02, 0.3, 0.02, 0.2, 0.02]
# words = ['长城', '汽车', '外观', '好看', '，', '但', '内饰', '不', '好看', '!']

# 这 手感 真是 差 了 点 ，
# attention = '0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.0613466203 0.50911963 0.0665089861 0.103029005 0.0657378137 0.131434217 0.0628237501'
# attention = '1.02608879e-20 1.02608879e-20 1.02608879e-20 1.02608879e-20 1.02608879e-20 1.02608879e-20 1.02608879e-20 1.02608879e-20 1.02608879e-20 1.02608879e-20 1.02608879e-20 1.02608879e-20 1.02608879e-20 1.02608879e-20 1.02608879e-20 1.02608879e-20 1.02608879e-20 1.02608879e-20 1.02608879e-20 1.02608879e-20 1.02608879e-20 1.02608879e-20 1.02608879e-20 1.02608879e-20 1.02608879e-20 1.02608879e-20 1.02608879e-20 1.02608879e-20 1.02608879e-20 1.02608879e-20 1.02608879e-20 1.02608879e-20 1.02608879e-20 1.02608879e-20 1.02608879e-20 1.02608879e-20 1.02608879e-20 3.54800015e-15 1 2.03665557e-12 2.9707823e-11 9.6052884e-15 1.91293249e-12 1.143457e-15'
# attention = '0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.128535792 0.135611549 0.136854082 0.138024524 0.142989114 0.146076918 0.171907946'
# attention = '3.02421691e-33 3.02421691e-33 3.02421691e-33 3.02421691e-33 3.02421691e-33 3.02421691e-33 3.02421691e-33 3.02421691e-33 3.02421691e-33 3.02421691e-33 3.02421691e-33 3.02421691e-33 3.02421691e-33 3.02421691e-33 3.02421691e-33 3.02421691e-33 3.02421691e-33 3.02421691e-33 3.02421691e-33 3.02421691e-33 3.02421691e-33 3.02421691e-33 3.02421691e-33 3.02421691e-33 3.02421691e-33 3.02421691e-33 3.02421691e-33 3.02421691e-33 3.02421691e-33 3.02421691e-33 3.02421691e-33 3.02421691e-33 3.02421691e-33 3.02421691e-33 3.02421691e-33 3.02421691e-33 3.02421691e-33 2.92929853e-22 9.07746653e-05 0.0514701866 0.927745 0.018308349 0.00238560862 2.69293377e-12'

# FOOD#QUALITY
attention = '0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.00192417449 0.0010443764 0.00215793145 0.0946626514 0.121935375 0.203474924 0.433941275 0.0016474413 0.00450814515 0.0368533432 0.0164593756 0.00382801471 0.00508477027 0.00412875507 0.00198703702 0.00184449169 0.00264574378 0.0072450866 0.00258829072 0.009709117 0.00318805105 0.00286209793 0.00365410466 0.00257883035 0.00201851712 0.00252715405 0.00406528078 0.00281116972 0.00339439767 0.0102817286 0.0049483804'
attention = '1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 1.75991949e-14 6.5960154e-10 2.73698529e-11 8.48761946e-12 1.21844301e-09 4.75145526e-07 0.00344584649 0.996553659 1.00778179e-11 2.01562386e-13 3.38797078e-13 4.78934448e-10 2.04757327e-12 1.13547068e-10 1.49316295e-10 3.23191508e-11 2.62777156e-09 1.2134839e-10 5.91892529e-14 6.40288877e-10 2.51411292e-09 2.35921283e-11 2.5361109e-11 1.85510461e-11 1.91971734e-11 3.34617264e-11 4.51006489e-11 5.63835827e-12 2.39737986e-11 6.05548528e-11 2.53495857e-12 6.04348212e-12'
attention = '0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.0272351205 0.0152827213 0.013818888 0.0167824142 0.024054151 0.0303471405 0.0395369455 0.0332924947 0.0286057778 0.0238897409 0.0235376619 0.0271908604 0.027438527 0.0298573077 0.022263201 0.037926659 0.0348853283 0.0299396142 0.0365083478 0.0371131599 0.0383604765 0.0358958766 0.0350235663 0.0357785821 0.0381739028 0.0407814868 0.0411421 0.0454885438 0.0436773151 0.0431461819 0.0430259183'
attention = '1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 1.54542889e-07 4.06064783e-06 2.30653632e-06 1.28179472e-05 2.79876258e-05 0.000588548311 0.0010519 0.0139173009 0.0158907827 0.00810222 0.00187343406 0.0705405101 0.00897636637 0.0155464364 0.0156693831 0.00685778353 0.136751175 0.490080833 0.0587632507 0.0632082373 0.0136493659 0.0631495491 0.00993498415 0.00255782972 0.00190584944 0.000403023558 0.000153249392 0.000291456498 3.92257207e-05 6.8983104e-06 4.40127877e-07 7.96573829e-08'

attention = attention.split()
attention = [float(e) for e in attention]

print(sum(attention))
words = 'excellent dumplings served amid clean chic decor got 10 10-piece dim sum combo every bite great but 1 small piece not worth wo n\'t go back unless someone else footing bill'.split()
attention = attention[len(words) * -1:]
while len(words) < len(attention):
    words = ['空'] + words

plt.bar(range(len(attention)), attention, tick_label=words)
plt.show()
print('')
