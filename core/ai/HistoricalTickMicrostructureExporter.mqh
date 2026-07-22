//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : HistoricalTickMicrostructureExporter.mqh               |
//| Layer   : Core / AI / Learning / Research                       |
//| Version : 1.0.0                                                  |
//| Purpose : Export completed M15 tick context by Dataset row       |
//+------------------------------------------------------------------+

#ifndef CORE_AI_HISTORICALTICKMICROSTRUCTUREEXPORTER_MQH
#define CORE_AI_HISTORICALTICKMICROSTRUCTUREEXPORTER_MQH

#include "storage/DatasetReader.mqh"
#include "../brain/liquidity/engines/TickMicrostructureEngine.mqh"

class CHistoricalTickMicrostructureExporter
  {
private:
   CTickMicrostructureEngine m_engine;

   bool WriteNeutral(const int handle,const CDatasetRecord &record,
                     const int tickCount) const
     {
      const int safeTickCount=(tickCount>0 ? tickCount : 0);
      return(FileWrite(handle,record.Id(),record.Timestamp(),
                       50.0,50.0,50.0,50.0,50.0,50.0,
                       safeTickCount,0.0)>0);
     }

public:
   datetime ObservationTime(const datetime barOpen,
                            const ENUM_TIMEFRAMES timeframe) const
     {
      const int seconds=PeriodSeconds(timeframe);
      if(barOpen<=0 || seconds<=0)
         return(0);
      return(barOpen+seconds);
     }

   bool IsBarClosed(const datetime barOpen,const datetime observationTime,
                    const ENUM_TIMEFRAMES timeframe) const
     {
      return(barOpen>0 && observationTime>0 &&
             barOpen+PeriodSeconds(timeframe)<=observationTime);
     }

   int Export(const string datasetFile,const string outputFile,
              const int progressInterval=100)
     {
      if(datasetFile=="" || outputFile=="" || progressInterval<=0)
         return(-1);
      CDatasetReader reader;
      if(!reader.Initialize(datasetFile))
         return(-1);
      if(FileIsExist(outputFile) && !FileDelete(outputFile))
        {
         reader.Shutdown();
         return(-1);
        }
      const int handle=FileOpen(outputFile,FILE_CSV|FILE_WRITE|FILE_ANSI,',');
      if(handle==INVALID_HANDLE)
        {
         reader.Shutdown();
         return(-1);
        }
      FileWrite(handle,"id","timestamp","tick_direction_imbalance",
                "tick_burst_concentration","mean_spread_atr",
                "maximum_spread_atr","realized_tick_volatility_atr",
                "tick_path_efficiency","tick_count",
                "tick_microstructure_valid");

      int atrHandle=INVALID_HANDLE;
      string atrSymbol="";
      int written=0;
      int valid=0;
      CDatasetRecord record;
      while(reader.Read(record))
        {
         if(atrHandle==INVALID_HANDLE)
           {
            atrSymbol=record.Symbol();
            atrHandle=iATR(atrSymbol,PERIOD_M15,14);
            if(atrHandle==INVALID_HANDLE)
              {
               FileClose(handle);
               reader.Shutdown();
               return(-1);
              }
           }
         if(record.Symbol()!=atrSymbol)
           {
            IndicatorRelease(atrHandle);
            FileClose(handle);
            reader.Shutdown();
            return(-1);
           }

         const datetime observation=ObservationTime(record.Timestamp(),PERIOD_M15);
         const int shift=iBarShift(record.Symbol(),PERIOD_M15,
                                   record.Timestamp(),true);
         if(shift<0 || !IsBarClosed(record.Timestamp(),observation,PERIOD_M15))
           {
            IndicatorRelease(atrHandle);
            FileClose(handle);
            reader.Shutdown();
            return(-1);
           }

         double atrBuffer[];
         MqlTick ticks[];
         const ulong fromMsc=(ulong)record.Timestamp()*1000;
         const ulong toMsc=(ulong)observation*1000-1;
         const int copied=CopyTicksRange(record.Symbol(),ticks,COPY_TICKS_ALL,
                                         fromMsc,toMsc);
         CTickMicrostructureResult result;
         if(copied>0 && CopyBuffer(atrHandle,0,shift,1,atrBuffer)==1 &&
            atrBuffer[0]>0.0)
            result=m_engine.Analyze(ticks,atrBuffer[0],record.Timestamp(),PERIOD_M15);

         bool rowWritten=false;
         if(!result.Valid)
            rowWritten=WriteNeutral(handle,record,copied);
         else
           {
            rowWritten=(FileWrite(
               handle,record.Id(),record.Timestamp(),
               result.TickDirectionImbalance,result.TickBurstConcentration,
               result.MeanSpreadAtr,result.MaximumSpreadAtr,
               result.RealizedTickVolatilityAtr,result.TickPathEfficiency,
               result.TickCount,100.0)>0);
            if(rowWritten)
               valid++;
           }
         if(!rowWritten)
           {
            IndicatorRelease(atrHandle);
            FileClose(handle);
            reader.Shutdown();
            return(-1);
           }
         written++;
         if(written%progressInterval==0)
           {
            FileFlush(handle);
            Print("Historical tick microstructure progress: ",written,
                  " records, valid: ",valid);
           }
        }
      if(atrHandle!=INVALID_HANDLE)
         IndicatorRelease(atrHandle);
      FileFlush(handle);
      FileClose(handle);
      reader.Shutdown();
      Print("Historical tick microstructure valid records: ",valid,"/",written);
      return(written);
     }
  };

#endif
