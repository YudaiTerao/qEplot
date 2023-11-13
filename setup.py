
from setuptools import setup, find_packages

setup(
    name="qEplot",
    version="0.2.0",
    author="Yudai Terao",
    packages=find_packages(),
    install_requires=[
        'plottool@git+https://github.com/YudaiTerao/plottool.git'
    ],
    entry_points={
        'console_scripts':[
            'qb = qEplot.banddos_plot:bandplot',
            'qbp = qEplot.banddos_plot:banddosplot',
            'qbc = qEplot.banddos_plot:qbwbplot',
            'qb-pdf = qEplot.banddos_plot_pdf:bandplot',
            'qbp-pdf = qEplot.banddos_plot_pdf:banddosplot',
            'qbc-pdf = qEplot.banddos_plot_pdf:qbwbplot',
        ],
    },
)

