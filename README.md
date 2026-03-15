# hyperface dataset

This dataset contains the raw data for
*hyperface: a naturalistic fMRI dataset to characterize human face processing*, by
Matteo Visconti di Oleggio Castello, Guo Jiahui, Ma Feilong, Manon de
Villemejane, James V. Haxby, and M. Ida Gobbini.

If you use this dataset or the code, please cite the corresponding
paper:

> Visconti di Oleggio Castello, M., Jiahui, G., Feilong, M., de
> Villemejane, M., Haxby, J. V., & Gobbini, M. I. (2026). *Hyperface: a
> naturalistic fMRI dataset for investigating human face processing*. In
> bioRxiv (p. 2026.03.11.711073). bioRxiv.
> https://doi.org/10.64898/2026.03.11.711073

See also this paper:

> Jiahui, G., Feilong, M., Visconti di Oleggio Castello, M., Nastase, S.A.,
> Haxby, J.V., & Gobbini, M.I. (2023). *Modeling naturalistic face processing
> in humans with deep convolutional neural networks*. Proceedings of the National
> Academy of Sciences. https://doi.org/10.1073/pnas.2304085120


Sample code for the QA analyses is available at
https://github.com/mvdoc/hyperface-data-paper.

The hyperface fMRIPrep derivatives are available at
https://openneuro.org/datasets/ds007384.

The hyperface FreeSurfer derivatives are available at
https://openneuro.org/datasets/ds007378.

## Associated papers and datasets

The Grand Budapest Hotel raw data is available at
https://openneuro.org/datasets/ds003017. See this paper for
more information:

> Visconti di Oleggio Castello, M., Chauhan, V., Jiahui, G., & Gobbini, M.
> I. (2020). *An fMRI dataset in response to "The Grand Budapest Hotel", a
> socially-rich, naturalistic movie*. Scientific Data, 7(1), 1-9.
> https://doi.org/10.1038/s41597-020-00735-4

The identity decoding raw data is available at
https://openneuro.org/datasets/ds003834. See this paper for more
information:

> Visconti di Oleggio Castello, M., Haxby, J.V., & Gobbini, M.I. (2021).
> *Shared neural codes for visual and semantic information about familiar
> faces in a common representational space*. Proceedings of the National
> Academy of Sciences. https://doi.org/10.1073/pnas.2110474118


## Notes

The dataset includes three sessions per participant:
- ses-1: Contains functional, fieldmap, DWI, and T2w anatomical data
- ses-2: Contains functional, fieldmap, and DWI data
- ses-budapest: Contains only T1w anatomical scans

The original budapest functional and fieldmap data have been removed from this
dataset. Users who need the complete dataset including budapest functional data can
use the merge script located under the code/ directory to combine this dataset with
the original budapest data from https://openneuro.org/datasets/ds003017
if needed.

All anatomicals (T1w, T2w) were defaced with `pydeface`.

## Contact information

For questions on this dataset, please contact Matteo Visconti di Oleggio
Castello (matteo.visconti@berkeley.edu).
