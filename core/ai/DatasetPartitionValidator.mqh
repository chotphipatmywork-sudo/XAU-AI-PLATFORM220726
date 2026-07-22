//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : DatasetPartitionValidator.mqh                          |
//| Layer   : Core / AI / Learning                                   |
//| Version : 4.0.0                                                  |
//| Purpose : Validate purged offline training dataset partitions    |
//+------------------------------------------------------------------+

#ifndef CORE_AI_DATASETPARTITIONVALIDATOR_MQH
#define CORE_AI_DATASETPARTITIONVALIDATOR_MQH

#include "models/DatasetPartitionValidationReport.mqh"
#include "storage/DatasetReader.mqh"

class CDatasetPartitionValidator
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

   void CountLabel(const int partition,const double label,CDatasetPartitionValidationReport &report) const
     {
      if(partition==0)
        {
         if(label==1.0) report.TrainBuyCount++;
         else if(label==0.0) report.TrainHoldCount++;
         else if(label==-1.0) report.TrainSellCount++;
         else report.InvalidLabelCount++;
        }
      else if(partition==1)
        {
         if(label==1.0) report.ValidationBuyCount++;
         else if(label==0.0) report.ValidationHoldCount++;
         else if(label==-1.0) report.ValidationSellCount++;
         else report.InvalidLabelCount++;
        }
      else
        {
         if(label==1.0) report.TestBuyCount++;
         else if(label==0.0) report.TestHoldCount++;
         else if(label==-1.0) report.TestSellCount++;
         else report.InvalidLabelCount++;
        }
     }

   bool ReadPartition(const string file_name,const int partition,long &ids[],datetime &timestamps[],CDatasetPartitionValidationReport &report) const
     {
      CDatasetReader reader;
      if(!reader.Initialize(file_name))
         return(false);

      int records=0;
      datetime previous_timestamp=0;
      datetime first_timestamp=0;
      datetime last_timestamp=0;
      CDatasetRecord record;
      while(reader.Read(record))
        {
         if(records>0 && record.Timestamp()<=previous_timestamp)
           {
            reader.Shutdown();
            return(false);
           }
         previous_timestamp=record.Timestamp();
         if(records==0)
            first_timestamp=record.Timestamp();
         last_timestamp=record.Timestamp();
         records++;

         if(ContainsId(ids,record.Id())) report.DuplicateIdCount++;
         else
           {
            const int size=ArraySize(ids);
            ArrayResize(ids,size+1);
            ids[size]=record.Id();
           }
         if(ContainsTimestamp(timestamps,record.Timestamp())) report.DuplicateTimestampCount++;
         else
           {
            const int size=ArraySize(timestamps);
            ArrayResize(timestamps,size+1);
            timestamps[size]=record.Timestamp();
         }

         const CAITrainingSample sample=record.Sample();
         const CAIFeatureVector features=sample.Features();
         if(!IsFeatureValid(features)) report.InvalidFeatureCount++;
         CountLabel(partition,sample.Label(),report);
        }
      reader.Shutdown();
      if(records<=0)
         return(false);

      if(partition==0)
        {
         report.TrainRecords=records;
         report.TrainFirstTimestamp=first_timestamp;
         report.TrainLastTimestamp=last_timestamp;
        }
      else if(partition==1)
        {
         report.ValidationRecords=records;
         report.ValidationFirstTimestamp=first_timestamp;
         report.ValidationLastTimestamp=last_timestamp;
        }
      else
        {
         report.TestRecords=records;
         report.TestFirstTimestamp=first_timestamp;
         report.TestLastTimestamp=last_timestamp;
        }
      return(true);
     }

public:
   bool Validate(const string train_file,const string validation_file,const string test_file,
                 CDatasetPartitionValidationReport &report,const int purge_bars=16,
                 const int bar_seconds=900) const
     {
      report.Reset();
      if(train_file=="" || validation_file=="" || test_file=="" || purge_bars<=0 || bar_seconds<=0 ||
         train_file==validation_file || train_file==test_file || validation_file==test_file)
         return(false);

      long ids[];
      datetime timestamps[];
      if(!ReadPartition(train_file,0,ids,timestamps,report) ||
         !ReadPartition(validation_file,1,ids,timestamps,report) ||
         !ReadPartition(test_file,2,ids,timestamps,report))
         return(false);

      report.TemporalOrderValid=(report.TrainLastTimestamp<report.ValidationFirstTimestamp &&
                                 report.ValidationLastTimestamp<report.TestFirstTimestamp);
      report.TrainValidationGapSeconds=(int)(report.ValidationFirstTimestamp-report.TrainLastTimestamp);
      report.ValidationTestGapSeconds=(int)(report.TestFirstTimestamp-report.ValidationLastTimestamp);
      const int minimum_gap_seconds=(purge_bars+1)*bar_seconds;
      report.PurgeBoundaryValid=(report.TrainValidationGapSeconds>=minimum_gap_seconds &&
                                 report.ValidationTestGapSeconds>=minimum_gap_seconds);
      report.Valid=(report.TemporalOrderValid && report.PurgeBoundaryValid && report.DuplicateIdCount==0 &&
                    report.DuplicateTimestampCount==0 && report.InvalidFeatureCount==0 &&
                    report.InvalidLabelCount==0);
      return(report.Valid);
     }
  };

#endif
