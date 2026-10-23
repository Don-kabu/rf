// Audit WorldCereal labels and Sentinel-2 observations for the Mbanza-Ngungu pilot.
// Paste this file into https://code.earthengine.google.com/ and click Run.
// Earth Engine account access is required. No export is started by this script.

var AOI = ee.Geometry.Rectangle(
  [14.813277, -5.303285, 14.903487, -5.213453], null, false
);
var AEZ_ID = 4010;
var LABEL_SEASON = 'tc-annual';
var LABEL_PRODUCT = 'temporarycrops';
var CONFIDENCE_SCREENING_THRESHOLD = 70; // Diagnostic only; compare 60/70/80 later.

Map.centerObject(AOI, 12);
Map.setOptions('SATELLITE');
Map.addLayer(AOI, {color: 'yellow'}, 'AOI — Mbanza-Ngungu');

// Season dates inferred from the AEZ 4010 calendar (DOY 291 to DOY 290).
// Earth Engine end dates are exclusive, so 2021-10-18 includes October 17.
var WINDOWS = [
  {name: 'WorldCereal temporary crops — annual season', start: '2020-10-17', end: '2021-10-18'},
  {name: 'WorldCereal maize — main season', start: '2021-02-12', end: '2021-08-03'}
];

function reportLabel(label) {
  print('Selected WorldCereal image properties', label.toDictionary([
    'system:index', 'aez_id', 'product', 'season'
  ]));
  print('WorldCereal bands', label.bandNames());

  var classification = label.select('classification').clip(AOI);
  var confidence = label.select('confidence').clip(AOI);
  Map.addLayer(classification, {
    min: 0, max: 100, palette: ['d8d8d8', '228b22']
  }, 'WorldCereal classes: 0=other, 100=crop');
  Map.addLayer(confidence, {
    min: 0, max: 100, palette: ['b2182b', 'fdd835', '1a9850']
  }, 'WorldCereal confidence (0–100)', false);

  // Count 10 m pixels and split the reference classes. Missing pixels are not
  // silently counted as class 0. WorldCereal documents classification values
  // of 0/100 and confidence values from 0 to 100.
  var valid = label.select('classification').mask().gt(0).unmask(0).clip(AOI);
  var classImage = label.select('classification');
  var confidenceValid = label.select('confidence')
    .updateMask(label.select('classification').mask());
  var countImage = ee.Image.cat([
    ee.Image.constant(1).rename('aoi_px').clip(AOI),
    valid.rename('label_valid_px'),
    classImage.eq(100).unmask(0).clip(AOI).rename('crop_100_px'),
    classImage.eq(0).unmask(0).clip(AOI).rename('other_0_px'),
    confidenceValid.gte(CONFIDENCE_SCREENING_THRESHOLD).unmask(0)
      .clip(AOI).rename('confidence_ge_threshold_px'),
    classImage.eq(100).and(confidenceValid.gte(CONFIDENCE_SCREENING_THRESHOLD))
      .unmask(0).clip(AOI).rename('crop_100_ge_threshold_px'),
    classImage.eq(0).and(confidenceValid.gte(CONFIDENCE_SCREENING_THRESHOLD))
      .unmask(0).clip(AOI).rename('other_0_ge_threshold_px')
  ]);
  var pixelCounts = countImage.reduceRegion({
    reducer: ee.Reducer.sum(),
    geometry: AOI,
    scale: 10,
    maxPixels: 1e9,
    tileScale: 4
  });
  print('WorldCereal pixel counts at 10 m', pixelCounts);
  print('WorldCereal coverage and class proportions (%)', ee.Dictionary({
    label_coverage_pct: ee.Number(pixelCounts.get('label_valid_px'))
      .divide(ee.Number(pixelCounts.get('aoi_px'))).multiply(100),
    crop_share_of_valid_pct: ee.Number(pixelCounts.get('crop_100_px'))
      .divide(ee.Number(pixelCounts.get('label_valid_px'))).multiply(100),
    other_share_of_valid_pct: ee.Number(pixelCounts.get('other_0_px'))
      .divide(ee.Number(pixelCounts.get('label_valid_px'))).multiply(100),
    confidence_threshold: CONFIDENCE_SCREENING_THRESHOLD,
    high_confidence_share_of_valid_pct: ee.Number(
      pixelCounts.get('confidence_ge_threshold_px')
    ).divide(ee.Number(pixelCounts.get('label_valid_px'))).multiply(100)
  }));
  print('WorldCereal confidence mean', confidenceValid.reduceRegion({
    reducer: ee.Reducer.mean(), geometry: AOI, scale: 10,
    maxPixels: 1e9, tileScale: 4
  }));
  print('WorldCereal confidence percentiles', confidenceValid.reduceRegion({
    reducer: ee.Reducer.percentile([10, 25, 50, 75, 90]),
    geometry: AOI, scale: 10, maxPixels: 1e9, tileScale: 4
  }));
}

var worldCereal = ee.ImageCollection('ESA/WorldCereal/2021/MODELS/v100')
  .filter(ee.Filter.eq('aez_id', AEZ_ID))
  .filter(ee.Filter.eq('product', LABEL_PRODUCT))
  .filter(ee.Filter.eq('season', LABEL_SEASON));

print('Nombre d’images WorldCereal correspondant aux filtres', worldCereal.size());
worldCereal.size().evaluate(function (numberOfImages) {
  if (!numberOfImages) {
    print('Aucun produit ne correspond. Vérifier aez_id, product et season dans la collection.');
    return;
  }
  reportLabel(ee.Image(worldCereal.first()));
});

// ESA SCL classes masked here: 0 no data, 1 defective/saturated, 3 cloud
// shadow, 7 low-probability cloud/unclassified, 8/9 cloud, 10 cirrus, 11 snow.
// SCL is 20 m; this audit uses 10 m B2 as its coverage grid. The screening
// threshold is a practical diagnostic, not an ESA-defined pass/fail rule.
function maskS2(image) {
  var scl = image.select('SCL');
  var clear = scl.neq(0)
    .and(scl.neq(1))
    .and(scl.neq(3))
    .and(scl.neq(7))
    .and(scl.neq(8))
    .and(scl.neq(9))
    .and(scl.neq(10))
    .and(scl.neq(11));
  return image.updateMask(clear)
    .select(['B2', 'B3', 'B4', 'B8'])
    .divide(10000)
    .copyProperties(image, ['system:time_start', 'CLOUDY_PIXEL_PERCENTAGE']);
}

function auditSentinelWindow(window) {
  var raw = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
    .filterBounds(AOI)
    .filterDate(window.start, window.end);
  var clear = raw.map(maskS2);
  print(window.name + ' — scènes Sentinel-2 qui intersectent l’emprise', raw.size());
  print(window.name + ' — dates des scènes', raw.aggregate_array('system:time_start')
    .map(function (date) { return ee.Date(date).format('YYYY-MM-dd'); }));

  var observationCount = clear.select('B2').count()
    .rename('clear_observations').unmask(0).clip(AOI);
  var s2CountImage = ee.Image.cat([
    ee.Image.constant(1).rename('aoi_px').clip(AOI),
    observationCount.gte(1).rename('pixels_ge_1_clear_obs'),
    observationCount.gte(3).rename('pixels_ge_3_clear_obs')
  ]);
  var coverageCounts = s2CountImage.reduceRegion({
    reducer: ee.Reducer.sum(), geometry: AOI, scale: 10,
    maxPixels: 1e9, tileScale: 4
  });
  var meanCount = observationCount.reduceRegion({
    reducer: ee.Reducer.mean(), geometry: AOI, scale: 10,
    maxPixels: 1e9, tileScale: 4
  });
  print(window.name + ' — couverture après masque SCL (%)', ee.Dictionary({
    aoi_pixels: coverageCounts.get('aoi_px'),
    pixels_with_1_or_more_clear_obs_pct: ee.Number(
      coverageCounts.get('pixels_ge_1_clear_obs')
    ).divide(ee.Number(coverageCounts.get('aoi_px'))).multiply(100),
    pixels_with_3_or_more_clear_obs_pct: ee.Number(
      coverageCounts.get('pixels_ge_3_clear_obs')
    ).divide(ee.Number(coverageCounts.get('aoi_px'))).multiply(100),
    mean_clear_observations_per_pixel: meanCount.get('clear_observations')
  }));

  var composite = clear.median().clip(AOI);
  Map.addLayer(composite, {
    bands: ['B4', 'B3', 'B2'], min: 0.02, max: 0.3
  }, window.name + ' — composite RGB', false);
  Map.addLayer(observationCount, {
    min: 0, max: 12, palette: ['8c2d04', 'fee08b', '1a9850']
  }, window.name + ' — nombre d’observations claires par pixel', false);
}

WINDOWS.forEach(auditSentinelWindow);

// To inspect the maize labels instead, change the label settings at the top to:
// LABEL_SEASON = 'tc-maize-main'; LABEL_PRODUCT = 'maize';
