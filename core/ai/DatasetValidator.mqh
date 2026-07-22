//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : DatasetValidator.mqh                                   |
//| Layer   : Core / AI / Learning                                   |
//| Version : 4.0.0                                                  |
//| Purpose : Validate offline AI training datasets                  |
//+------------------------------------------------------------------+

#ifndef CORE_AI_DATASETVALIDATOR_MQH
#define CORE_AI_DATASETVALIDATOR_MQH

#include "models/DatasetValidationReport.mqh"
#include "storage/DatasetReader.mqh"

class CDatasetValidator
  {
private:
   bool IsFeatureValid(const CAIFeatureVector &features) const
     {
      return(features.TrendRegime>=0.0 && features.TrendRegime<=100.0 &&
             features.TrendMomentum>=0.0 && features.TrendMomentum<=100.0 &&
             features.TrendSlope>=0.0 && features.TrendSlope<=100.0 &&
             features.VolatilityRegime>=0.0 && features.VolatilityRegime<=100.0 &&
             features.VolatilityChange>=0.0 && features.VolatilityChange<=100.0 &&
             features.LiquidityActivity>=0.0 && features.LiquidityActivity<=100.0 &&
             features.LiquidityRangePosition>=0.0 && features.LiquidityRangePosition<=100.0 &&
             features.LiquiditySweepDirection>=0.0 && features.LiquiditySweepDirection<=100.0 &&
             (features.LiquiditySweepDirection==0.0 ||
              features.LiquiditySweepDirection==50.0 ||
              features.LiquiditySweepDirection==100.0) &&
             features.SessionAsia>=0.0 && features.SessionAsia<=100.0 &&
             features.SessionLondon>=0.0 && features.SessionLondon<=100.0 &&
             features.SessionNewYork>=0.0 && features.SessionNewYork<=100.0 &&
             (features.SessionAsia==0.0 || features.SessionAsia==100.0) &&
             (features.SessionLondon==0.0 || features.SessionLondon==100.0) &&
             (features.SessionNewYork==0.0 || features.SessionNewYork==100.0) &&
             features.SessionAsia+features.SessionLondon+features.SessionNewYork==100.0 &&
             features.SessionProgress>=0.0 && features.SessionProgress<=100.0);
     }

   bool ContainsId(const long &ids[],const long id) const
     {
      for(int index=0; index<ArraySize(ids); index++)
         if(ids[index]==id)
            return(true);
      return(false);
     }

   bool ContainsTimestamp(const datetime &timestamps[],const datetime timestamp) const
     {
      for(int index=0; index<ArraySize(timestamps); index++)
         if(timestamps[index]==timestamp)
            return(true);
      return(false);
     }

public:
   bool Validate(const string file_name,CDatasetValidationReport &report) const
     {
      report.Reset();
      CDatasetReader reader;
      if(!reader.Initialize(file_name))
         return(false);

      long ids[];
      datetime timestamps[];
      CDatasetRecord record;
      while(reader.Read(record))
        {
         report.TotalRecords++;
         if(ContainsId(ids,record.Id()))
            report.DuplicateIdCount++;
         else
           {
            const int size=ArraySize(ids);
            ArrayResize(ids,size+1);
            ids[size]=record.Id();
           }

         if(ContainsTimestamp(timestamps,record.Timestamp()))
            report.DuplicateTimestampCount++;
         else
           {
            const int size=ArraySize(timestamps);
            ArrayResize(timestamps,size+1);
            timestamps[size]=record.Timestamp();
           }

         const CAITrainingSample sample=record.Sample();
         const CAIFeatureVector features=sample.Features();
         if(!IsFeatureValid(features))
            report.InvalidFeatureCount++;

         const double label=sample.Label();
         if(label==1.0)
            report.BuyCount++;
         else if(label==0.0)
            report.HoldCount++;
         else if(label==-1.0)
            report.SellCount++;
         else
            report.InvalidLabelCount++;
        }
      reader.Shutdown();
      report.Valid=(report.TotalRecords>0 &&
                    report.DuplicateIdCount==0 &&
                    report.DuplicateTimestampCount==0 &&
                    report.InvalidFeatureCount==0 &&
                    report.InvalidLabelCount==0);
      return(true);
     }
  };

#endif
