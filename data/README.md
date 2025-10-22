# Sample Dataset Information

Place your agricultural datasets in the appropriate folders:

## CSV Files (data/raw/csvs/)
- Crop yield data
- Soil nutrient analysis
- Weather records
- Historical agricultural data

**Example CSV structure for yield prediction:**
```
nitrogen,phosphorus,potassium,rainfall,temperature,ph,yield
90,42,43,202.9,26.8,6.5,3.4
85,38,40,198.5,25.2,6.8,3.1
...
```

## PDF Files (data/raw/pdfs/)
- Agricultural research papers
- Farming best practices guides
- Government agricultural reports
- Extension service materials

## Image Files (data/raw/images/)
- Crop disease images
- Pest identification photos
- Healthy crop references
- Field condition photos

**Recommended folder structure for images:**
```
data/raw/images/
├── healthy/
├── disease_type_1/
├── disease_type_2/
└── ...
```

## Data Sources

### Recommended Datasets
1. **Kaggle Datasets**:
   - Crop Recommendation Dataset
   - Plant Disease Dataset
   - Agricultural Production Data

2. **Government Sources**:
   - USDA Agricultural Statistics
   - FAO Country Stats
   - National Agricultural Research Systems

3. **Research Institutions**:
   - University agricultural departments
   - Research stations
   - Extension services

## Data Privacy

⚠️ **Important**: Ensure you have proper rights to use any data. Don't commit sensitive or proprietary data to version control.

## Next Steps

1. Download datasets from recommended sources
2. Place in appropriate folders
3. Run preprocessing scripts
4. Validate data quality
5. Start model training

---

**Note**: Raw data files are ignored by git (see `.gitignore`)
