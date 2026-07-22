//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : DatasetRecord.mqh                                      |
//| Layer   : Core / AI / Learning                                   |
//| Version : 1.0.0                                                  |
//| Purpose : Persistable training sample metadata                   |
//+------------------------------------------------------------------+

#ifndef CORE_AI_MODELS_DATASETRECORD_MQH
#define CORE_AI_MODELS_DATASETRECORD_MQH

#include "AITrainingSample.mqh"

class CDatasetRecord
  {
private:
   long              m_id;
   datetime          m_timestamp;
   string            m_symbol;
   CAITrainingSample m_sample;

public:
   CDatasetRecord(void)
     {
      Reset();
     }

   void Reset(void)
     {
      m_id=0;
      m_timestamp=0;
      m_symbol="";
      m_sample.Reset();
     }

   void Set(const long id,const datetime timestamp,const string symbol,const CAITrainingSample &sample)
     {
      m_id=id;
      m_timestamp=timestamp;
      m_symbol=symbol;
      m_sample=sample;
     }

   long Id(void) const { return(m_id); }
   datetime Timestamp(void) const { return(m_timestamp); }
   string Symbol(void) const { return(m_symbol); }
   CAITrainingSample Sample(void) const { return(m_sample); }
  };

#endif
