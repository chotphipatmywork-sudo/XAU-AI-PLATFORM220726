//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : DatasetSplitter.mqh                                    |
//| Layer   : Core / AI / Learning                                   |
//| Version : 1.1.0                                                  |
//| Purpose : Split an ordered dataset with label-horizon purging    |
//+------------------------------------------------------------------+

#ifndef CORE_AI_DATASETSPLITTER_MQH
#define CORE_AI_DATASETSPLITTER_MQH

#include "models/DatasetSplitConfig.mqh"
#include "models/DatasetSplitReport.mqh"
#include "storage/DatasetReader.mqh"
#include "storage/DatasetWriter.mqh"

class CDatasetSplitter
  {
private:
   bool CountOrderedRecords(const string file_name,int &total_records) const
     {
      total_records=0;
      CDatasetReader reader;
      if(!reader.Initialize(file_name))
         return(false);

      datetime previous_timestamp=0;
      CDatasetRecord record;
      while(reader.Read(record))
        {
         if(total_records>0 && record.Timestamp()<=previous_timestamp)
           {
            reader.Shutdown();
            return(false);
           }
         previous_timestamp=record.Timestamp();
         total_records++;
        }
      reader.Shutdown();
      return(total_records>0);
     }

public:
   bool Split(const string input_file,
              const string train_file,
              const string validation_file,
              const string test_file,
              const CDatasetSplitConfig &config,
              CDatasetSplitReport &report) const
     {
      report.Reset();
      if(!config.IsValid() || input_file=="" || train_file=="" ||
         validation_file=="" || test_file=="" || input_file==train_file ||
         input_file==validation_file || input_file==test_file ||
         train_file==validation_file || train_file==test_file || validation_file==test_file)
         return(false);

      int total_records=0;
      if(!CountOrderedRecords(input_file,total_records))
         return(false);

      const int train_boundary=(int)MathFloor(total_records*config.TrainRatio);
      const int validation_records=(int)MathFloor(total_records*config.ValidationRatio);
      const int validation_boundary=train_boundary+validation_records;
      const int train_write_end=train_boundary-config.PurgeBars;
      const int validation_write_end=validation_boundary-config.PurgeBars;
      if(train_write_end<=0 || validation_write_end<=train_boundary ||
         total_records-validation_boundary<=0)
         return(false);

      CDatasetReader reader;
      CDatasetWriter train_writer;
      CDatasetWriter validation_writer;
      CDatasetWriter test_writer;
      if(!reader.Initialize(input_file) ||
         !train_writer.Initialize(train_file,false) ||
         !validation_writer.Initialize(validation_file,false) ||
         !test_writer.Initialize(test_file,false))
        {
         reader.Shutdown();
         train_writer.Shutdown();
         validation_writer.Shutdown();
         test_writer.Shutdown();
         return(false);
        }

      int index=0;
      CDatasetRecord record;
      while(reader.Read(record))
        {
         bool written=true;
         if(index<train_write_end)
           {
            written=train_writer.Write(record);
            if(written)
              {
               if(report.TrainRecords==0) report.TrainFirstTimestamp=record.Timestamp();
               report.TrainRecords++;
               report.TrainLastTimestamp=record.Timestamp();
              }
           }
         else if(index<train_boundary)
           {
            report.PurgedRecords++;
           }
         else if(index<validation_write_end)
           {
            written=validation_writer.Write(record);
            if(written)
              {
               if(report.ValidationRecords==0) report.ValidationFirstTimestamp=record.Timestamp();
               report.ValidationRecords++;
               report.ValidationLastTimestamp=record.Timestamp();
              }
           }
         else if(index<validation_boundary)
           {
            report.PurgedRecords++;
           }
         else
           {
            written=test_writer.Write(record);
            if(written)
              {
               if(report.TestRecords==0) report.TestFirstTimestamp=record.Timestamp();
               report.TestRecords++;
               report.TestLastTimestamp=record.Timestamp();
              }
           }
         if(!written)
           {
            reader.Shutdown();
            train_writer.Shutdown();
            validation_writer.Shutdown();
            test_writer.Shutdown();
            return(false);
           }
         index++;
        }

      reader.Shutdown();
      train_writer.Shutdown();
      validation_writer.Shutdown();
      test_writer.Shutdown();
      report.TotalRecords=total_records;
      report.PurgeBarsPerBoundary=config.PurgeBars;
      report.Valid=(report.TrainRecords==train_write_end &&
                    report.ValidationRecords==validation_write_end-train_boundary &&
                    report.TestRecords==total_records-validation_boundary &&
                    report.PurgedRecords==config.PurgeBars*2 &&
                    report.TrainRecords+report.ValidationRecords+report.TestRecords+
                    report.PurgedRecords==total_records);
      return(report.Valid);
     }
  };

#endif
