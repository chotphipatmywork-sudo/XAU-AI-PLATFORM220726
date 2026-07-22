//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : DatasetReader.mqh                                      |
//| Layer   : Core / AI / Learning                                   |
//| Version : 4.0.0                                                  |
//| Purpose : Read training records from an offline dataset          |
//+------------------------------------------------------------------+

#ifndef CORE_AI_STORAGE_DATASETREADER_MQH
#define CORE_AI_STORAGE_DATASETREADER_MQH

#include "../models/DatasetRecord.mqh"

class CDatasetReader
  {
private:
   int  m_handle;
   bool m_initialized;

public:
   CDatasetReader(void)
     {
      m_handle=INVALID_HANDLE;
      m_initialized=false;
     }

   bool Initialize(const string file_name)
     {
      Shutdown();
      m_handle=FileOpen(file_name,FILE_CSV|FILE_READ|FILE_ANSI,',');
      if(m_handle==INVALID_HANDLE)
         return(false);
      for(int column=0; column<16; column++)
         FileReadString(m_handle);
      m_initialized=true;
      return(true);
     }

   bool Read(CDatasetRecord &record)
     {
      if(!m_initialized || FileIsEnding(m_handle))
         return(false);
      const long id=(long)StringToInteger(FileReadString(m_handle));
      const datetime timestamp=StringToTime(FileReadString(m_handle));
      const string symbol=FileReadString(m_handle);
      CAIFeatureVector features;
      features.TrendRegime=StringToDouble(FileReadString(m_handle));
      features.TrendMomentum=StringToDouble(FileReadString(m_handle));
      features.TrendSlope=StringToDouble(FileReadString(m_handle));
      features.VolatilityRegime=StringToDouble(FileReadString(m_handle));
      features.VolatilityChange=StringToDouble(FileReadString(m_handle));
      features.LiquidityActivity=StringToDouble(FileReadString(m_handle));
      features.LiquidityRangePosition=StringToDouble(FileReadString(m_handle));
      features.LiquiditySweepDirection=StringToDouble(FileReadString(m_handle));
      features.SessionAsia=StringToDouble(FileReadString(m_handle));
      features.SessionLondon=StringToDouble(FileReadString(m_handle));
      features.SessionNewYork=StringToDouble(FileReadString(m_handle));
      features.SessionProgress=StringToDouble(FileReadString(m_handle));
      CAITrainingSample sample;
      sample.SetFeatures(features);
      sample.SetLabel(StringToDouble(FileReadString(m_handle)));
      record.Set(id,timestamp,symbol,sample);
      return(true);
     }

   void Shutdown(void)
     {
      if(m_handle!=INVALID_HANDLE)
         FileClose(m_handle);
      m_handle=INVALID_HANDLE;
      m_initialized=false;
     }
  };

#endif
