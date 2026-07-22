//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : DatasetWriter.mqh                                      |
//| Layer   : Core / AI / Learning                                   |
//| Version : 4.0.0                                                  |
//| Purpose : Write training records to an offline dataset           |
//+------------------------------------------------------------------+

#ifndef CORE_AI_STORAGE_DATASETWRITER_MQH
#define CORE_AI_STORAGE_DATASETWRITER_MQH

#include "../models/DatasetRecord.mqh"

class CDatasetWriter
  {
private:
   int  m_handle;
   bool m_initialized;

public:
   CDatasetWriter(void)
     {
      m_handle=INVALID_HANDLE;
      m_initialized=false;
     }

   bool Initialize(const string file_name,const bool append)
     {
      Shutdown();
      if(!append && FileIsExist(file_name) && !FileDelete(file_name))
         return(false);
      m_handle=FileOpen(file_name,FILE_CSV|FILE_READ|FILE_WRITE|FILE_ANSI,',');
      if(m_handle==INVALID_HANDLE)
         return(false);
      if(FileSize(m_handle)==0)
         FileWrite(m_handle,"id","timestamp","symbol","trend_regime","trend_momentum","trend_slope","volatility_regime","volatility_change","liquidity_activity","liquidity_range_position","liquidity_sweep_direction","session_asia","session_london","session_new_york","session_progress","label");
      FileSeek(m_handle,0,SEEK_END);
      m_initialized=true;
      return(true);
     }

   bool Write(const CDatasetRecord &record)
     {
      if(!m_initialized)
         return(false);
      CAITrainingSample sample=record.Sample();
      CAIFeatureVector features=sample.Features();
      const uint written=FileWrite(m_handle,record.Id(),record.Timestamp(),record.Symbol(),features.TrendRegime,features.TrendMomentum,features.TrendSlope,features.VolatilityRegime,features.VolatilityChange,features.LiquidityActivity,features.LiquidityRangePosition,features.LiquiditySweepDirection,features.SessionAsia,features.SessionLondon,features.SessionNewYork,features.SessionProgress,sample.Label());
      return(written>0);
     }

   bool Flush(void)
     {
      if(!m_initialized)
         return(false);
      FileFlush(m_handle);
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
