//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : DatasetReadinessGate.mqh                               |
//| Layer   : Core / AI / Learning                                   |
//| Version : 1.0.0                                                  |
//| Purpose : Assess offline dataset readiness for model training    |
//+------------------------------------------------------------------+

#ifndef CORE_AI_DATASETREADINESSGATE_MQH
#define CORE_AI_DATASETREADINESSGATE_MQH

#include "DatasetPartitionValidator.mqh"
#include "models/DatasetReadinessConfig.mqh"
#include "models/DatasetReadinessReport.mqh"

class CDatasetReadinessGate
  {
private:
   bool HasMinimumLabels(const CDatasetPartitionValidationReport &partition_report,const int minimum) const
     {
      return(partition_report.TrainBuyCount>=minimum &&
             partition_report.TrainHoldCount>=minimum &&
             partition_report.TrainSellCount>=minimum &&
             partition_report.ValidationBuyCount>=minimum &&
             partition_report.ValidationHoldCount>=minimum &&
             partition_report.ValidationSellCount>=minimum &&
             partition_report.TestBuyCount>=minimum &&
             partition_report.TestHoldCount>=minimum &&
             partition_report.TestSellCount>=minimum);
     }

public:
   bool Evaluate(const string train_file,
                 const string validation_file,
                 const string test_file,
                 const CDatasetReadinessConfig &config,
                 CDatasetReadinessReport &report) const
     {
      report.Reset();
      if(!config.IsValid())
         return(false);

      CDatasetPartitionValidator validator;
      CDatasetPartitionValidationReport partition_report;
      if(!validator.Validate(train_file,validation_file,test_file,partition_report))
         return(false);

      report.PartitionValid=partition_report.Valid;
      report.TotalRecords=partition_report.TrainRecords+
                          partition_report.ValidationRecords+
                          partition_report.TestRecords;
      report.MeetsSizeRequirement=(report.TotalRecords>=config.MinimumTotalRecords &&
                                   partition_report.TrainRecords>=config.MinimumTrainRecords &&
                                   partition_report.ValidationRecords>=config.MinimumValidationRecords &&
                                   partition_report.TestRecords>=config.MinimumTestRecords);
      report.MeetsLabelCoverage=HasMinimumLabels(partition_report,config.MinimumLabelCountPerPartition);
      report.Ready=(report.PartitionValid && report.MeetsSizeRequirement && report.MeetsLabelCoverage);
      return(true);
     }
  };

#endif
