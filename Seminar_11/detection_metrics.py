import csv
import os
import numpy as np
from pycocotools.coco import COCO
from pycocotools.cocoeval import COCOeval

AP_AR_per_IoU = {
    'Average Precision  (AP) @[ IoU=0.50:0.95 | area=   all | maxDets=100 ]': 0.0,
    'Average Precision  (AP) @[ IoU=0.50      | area=   all | maxDets=100 ]': 0.0,
    'Average Precision  (AP) @[ IoU=0.75      | area=   all | maxDets=100 ]': 0.0,
    'Average Precision  (AP) @[ IoU=0.50:0.95 | area= small | maxDets=100 ]': 0.0,
    'Average Precision  (AP) @[ IoU=0.50:0.95 | area=medium | maxDets=100 ]': 0.0,
    'Average Precision  (AP) @[ IoU=0.50:0.95 | area= large | maxDets=100 ]': 0.0,
    'Average Recall     (AR) @[ IoU=0.50:0.95 | area=   all | maxDets=  1 ]': 0.0,
    'Average Recall     (AR) @[ IoU=0.50:0.95 | area=   all | maxDets= 10 ]': 0.0,
    'Average Recall     (AR) @[ IoU=0.50:0.95 | area=   all | maxDets=100 ]': 0.0,
    'Average Recall     (AR) @[ IoU=0.50:0.95 | area= small | maxDets=100 ]': 0.0,
    'Average Recall     (AR) @[ IoU=0.50:0.95 | area=medium | maxDets=100 ]': 0.0,
    'Average Recall     (AR) @[ IoU=0.50:0.95 | area= large | maxDets=100 ]': 0.0,
}


def coco_eval(
    result_files,
    coco,
    result_types=['segm'],
    classwise=True,
):
    for res_type in result_types:
        assert res_type in [
            'proposal', 'proposal_fast', 'bbox', 'segm', 'keypoints'
        ]

    if isinstance(coco, str):
        coco = COCO(coco)
        
    assert isinstance(coco, COCO)

    for res_type in result_types:
        if isinstance(result_files, str):
            result_file = result_files
        elif isinstance(result_files, dict):
            result_file = result_files[res_type]
        else:
            assert TypeError('result_files must be a str or dict')
        assert result_file.endswith('.json')

        coco_dets = coco.loadRes(result_file)
        img_ids = coco.getImgIds()
        iou_type = 'bbox' if res_type == 'proposal' else res_type
        cocoEval = COCOeval(coco, coco_dets, iou_type)
        cocoEval.params.imgIds = img_ids
        cocoEval.evaluate()
        cocoEval.accumulate()
        cocoEval.summarize()

        results_per_category = []
        if classwise:
            # Compute per-category AP
            # from https://github.com/facebookresearch/detectron2/blob/03064eb5bafe4a3e5750cc7a16672daf5afe8435/detectron2/evaluation/coco_evaluation.py#L259-L283 # noqa
            precisions = cocoEval.eval['precision']
            catIds = coco.getCatIds()
            # precision has dims (iou, recall, cls, area range, max dets)
            assert len(catIds) == precisions.shape[2]

            for idx, catId in enumerate(catIds):
                # area range index 0: all area ranges
                # max dets index -1: typically 100 per image
                nm = coco.loadCats(catId)[0]
                precision = precisions[:, :, idx, 0, -1]
                precision = precision[precision > -1]
                ap = np.mean(precision) if precision.size else float('nan')
                results_per_category.append(
                    ('{}'.format(nm['name']),
                     '{:0.3f}'.format(float(ap * 100))))

        return cocoEval.stats, results_per_category


def main():

    result_files = 'epoch_30_test_00_00.segm.json'
    coco = f'test_00_00_instances.json'
    stats, results_per_category = coco_eval(result_files, coco)

    for i, k in enumerate(AP_AR_per_IoU):
        AP_AR_per_IoU[k] = round(stats[i], 4)

    ap05095 = AP_AR_per_IoU['Average Precision  (AP) @[ IoU=0.50:0.95 | area=   all | maxDets=100 ]']
    ap05 = AP_AR_per_IoU['Average Precision  (AP) @[ IoU=0.50      | area=   all | maxDets=100 ]']
    ap075 = AP_AR_per_IoU['Average Precision  (AP) @[ IoU=0.75      | area=   all | maxDets=100 ]']
    ap05095large = AP_AR_per_IoU['Average Precision  (AP) @[ IoU=0.50:0.95 | area= large | maxDets=100 ]']

    aps_list = aps.split(' ')
    for ap in aps_list:
        print(ap)

    results = {
        'AP_AR_per_IoU': AP_AR_per_IoU,
        'AP_per_category': results_per_category,
    }

    with open('test_metrics.csv', mode='a') as f:
        f = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        f.writerow(['test', ap05095, ap05, ap075, ap05095large, apchair])

if __name__ == "__main__":
    main()
