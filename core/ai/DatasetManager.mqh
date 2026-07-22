//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : DatasetManager.mqh                                     |
//| Layer   : Core / AI / Learning                                   |
//| Version : 1.2.0                                                  |
//| Purpose : Coordinate offline training dataset access             |
//+------------------------------------------------------------------+

#ifndef CORE_AI_DATASETMANAGER_MQH
#define CORE_AI_DATASETMANAGER_MQH

#include "models/DatasetRecord.mqh"
#include "storage/DatasetWriter.mqh"
#include "storage/DatasetReader.mqh"

class CDatasetManager
  {
private:
   CDatasetWriter m_writer;
   CDatasetReader m_reader;
   string         m_file_name;
   long           m_next_id;
   bool           m_initialized;
   bool           m_write_mode;
   bool           m_append_mode;

   bool OpenWriter(void)
     {
      if(m_write_mode)
         return(true);
      m_reader.Shutdown();
      if(!m_writer.Initialize(m_file_name,true))
         return(false);
      m_append_mode=true;
      m_write_mode=true;
      return(true);
     }

public:
   CDatasetManager(void)
     {
      m_file_name="";
      m_next_id=1;
      m_initialized=false;
      m_write_mode=false;
      m_append_mode=false;
     }

   bool Initialize(const string file_name,const bool append=true)
     {
      Shutdown();
      m_file_name=file_name;
      m_append_mode=append;
      m_next_id=1;
      if(append && FileIsExist(m_file_name))
        {
         if(!m_reader.Initialize(m_file_name))
            return(false);
         CDatasetRecord record;
         while(m_reader.Read(record))
            if(record.Id()>=m_next_id)
               m_next_id=record.Id()+1;
         m_reader.Shutdown();
        }
      if(!m_writer.Initialize(m_file_name,m_append_mode))
         return(false);
      m_initialized=true;
      m_write_mode=true;
      return(true);
     }

   bool Append(const CAIFeatureVector &features,const double label,const string symbol,const datetime timestamp)
     {
      if(!m_initialized || !OpenWriter())
         return(false);
      CAITrainingSample sample;
      sample.SetFeatures(features);
      sample.SetLabel(label);
      CDatasetRecord record;
      record.Set(m_next_id++,timestamp,symbol,sample);
      return(m_writer.Write(record));
     }

   bool Flush(void)
     {
      if(!m_initialized || !m_write_mode)
         return(false);
      return(m_writer.Flush());
     }

   bool BeginRead(void)
     {
      if(!m_initialized)
         return(false);
      m_writer.Shutdown();
      if(!m_reader.Initialize(m_file_name))
         return(false);
      m_write_mode=false;
      return(true);
     }

   bool ReadNext(CDatasetRecord &record)
     {
      if(!m_initialized || m_write_mode)
         return(false);
      return(m_reader.Read(record));
     }

   void Shutdown(void)
     {
      m_writer.Shutdown();
      m_reader.Shutdown();
      m_initialized=false;
      m_write_mode=false;
      m_append_mode=false;
     }
  };

#endif
