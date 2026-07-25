//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : PastOnlyTriggerEventExporter.mqh                       |
//| Layer   : Core / AI / Learning / Offline Research                |
//| Version : 1.1.0                                                   |
//| Purpose : Export causal M5 trigger-event evidence for Train       |
//+------------------------------------------------------------------+

#ifndef CORE_AI_PASTONLYTRIGGEREVENTEXPORTER_MQH
#define CORE_AI_PASTONLYTRIGGEREVENTEXPORTER_MQH

#include "../brain/Brain.mqh"

class CPastOnlyTriggerEventExporter
  {
private:
   CBrain m_brain;

   bool ReadAndValidateHeader(const int handle) const
     {
      const string expected[]={
         "request_schema_version","request_id","observation_time",
         "symbol","direction","entry_bar_open","context_bar_open",
         "expected_entry","reference_poi","structural_stop",
         "nearest_target","expected_sweep_penetration_atr",
         "expected_reclaim_distance_atr","point_size",
         "lookback_m5_bars","deployment_authorized"
      };
      for(int index=0; index<ArraySize(expected); index++)
         if(FileReadString(handle)!=expected[index])
            return(false);
      return(true);
     }

   int AbortExport(const int input_handle,const int output_handle,
                   const string output_file,const string reason)
     {
      if(input_handle!=INVALID_HANDLE)
         FileClose(input_handle);
      if(output_handle!=INVALID_HANDLE)
         FileClose(output_handle);
      if(FileIsExist(output_file))
         FileDelete(output_file);
      m_brain.Shutdown();
      Print("Past-only trigger-event export failed closed: ",reason);
      return(-1);
     }

   bool EnsureHistory(const string symbol,const datetime entry_bar_open,
                      const int required_bars) const
     {
      MqlRates rates[];
      int copied=-1;
      int last_error=0;
      for(int attempt=0; attempt<40; attempt++)
        {
         ResetLastError();
         copied=CopyRates(symbol,PERIOD_M5,entry_bar_open,required_bars,rates);
         last_error=GetLastError();
         if(copied>=required_bars)
            return(true);
         Sleep(250);
        }
      Print("Past-only trigger-event history unavailable: symbol=",symbol,
            " entry=",TimeToString(entry_bar_open)," copied=",copied,
            " required=",required_bars," error=",last_error,
            " terminal_max_bars=",TerminalInfoInteger(TERMINAL_MAXBARS));
      return(false);
     }

   bool LoadKnownBars(const string symbol,const int entry_shift,
                      const int lookback,double &highs[],double &lows[]) const
     {
      const int count=lookback+3;
      ArrayResize(highs,count);
      ArrayResize(lows,count);
      for(int index=0; index<count; index++)
        {
         const int shift=entry_shift+index;
         const datetime bar_open=iTime(symbol,PERIOD_M5,shift);
         const double open=iOpen(symbol,PERIOD_M5,shift);
         const double high=iHigh(symbol,PERIOD_M5,shift);
         const double low=iLow(symbol,PERIOD_M5,shift);
         const double close=iClose(symbol,PERIOD_M5,shift);
         if(bar_open<=0 || open<=0.0 || high<=0.0 || low<=0.0 ||
            close<=0.0 || high<low || high<MathMax(open,close) ||
            low>MathMin(open,close))
            return(false);
         highs[index]=high;
         lows[index]=low;
        }
      return(true);
     }

public:
   bool ExactTiming(const datetime context_bar_open,
                    const datetime entry_bar_open,
                    const datetime observation) const
     {
      const int seconds=PeriodSeconds(PERIOD_M5);
      return(context_bar_open>0 && entry_bar_open>0 && observation>0 &&
             seconds>0 && context_bar_open+seconds==entry_bar_open &&
             entry_bar_open+seconds==observation);
     }

   bool ValidGeometry(const string direction,const double entry,
                      const double reference_poi,const double structural_stop,
                      const double nearest_target,const double point_size) const
     {
      const bool buy=(direction=="TRADE_SETUP_BUY");
      const bool sell=(direction=="TRADE_SETUP_SELL");
      if((!buy && !sell) || entry<=0.0 || reference_poi<=0.0 ||
         structural_stop<=0.0 || nearest_target<=0.0 || point_size<=0.0)
         return(false);
      return((buy && structural_stop<reference_poi &&
              reference_poi<entry && entry<nearest_target) ||
             (sell && nearest_target<entry && entry<reference_poi &&
              reference_poi<structural_stop));
     }

   bool CalculateBarShape(const string direction,const double open,
                          const double high,const double low,const double close,
                          const double atr,double &range_atr,double &body_atr,
                          double &directional_body_atr,double &upper_wick_atr,
                          double &lower_wick_atr,double &close_location) const
     {
      const bool buy=(direction=="TRADE_SETUP_BUY");
      const bool sell=(direction=="TRADE_SETUP_SELL");
      if((!buy && !sell) || open<=0.0 || high<=0.0 || low<=0.0 ||
         close<=0.0 || atr<=0.0 || high<=low ||
         high<MathMax(open,close) || low>MathMin(open,close))
         return(false);
      range_atr=(high-low)/atr;
      body_atr=MathAbs(close-open)/atr;
      directional_body_atr=(buy ? close-open : open-close)/atr;
      upper_wick_atr=(high-MathMax(open,close))/atr;
      lower_wick_atr=(MathMin(open,close)-low)/atr;
      close_location=(close-low)/(high-low);
      return(MathIsValidNumber(range_atr) && MathIsValidNumber(body_atr) &&
             MathIsValidNumber(directional_body_atr) &&
             MathIsValidNumber(upper_wick_atr) &&
             MathIsValidNumber(lower_wick_atr) &&
             MathIsValidNumber(close_location) && range_atr>0.0 &&
             upper_wick_atr>=0.0 && lower_wick_atr>=0.0 &&
             close_location>=0.0 && close_location<=1.0);
     }

   bool DirectionalEvidence(const string direction,const double high,
                            const double low,const double close,
                            const double reference_poi,const double atr,
                            double &sweep_atr,double &reclaim_atr) const
     {
      const bool buy=(direction=="TRADE_SETUP_BUY");
      const bool sell=(direction=="TRADE_SETUP_SELL");
      if((!buy && !sell) || high<=0.0 || low<=0.0 || close<=0.0 ||
         reference_poi<=0.0 || atr<=0.0 || high<low)
         return(false);
      sweep_atr=(buy ? MathMax(0.0,(reference_poi-low)/atr)
                     : MathMax(0.0,(high-reference_poi)/atr));
      reclaim_atr=(buy ? MathMax(0.0,(close-reference_poi)/atr)
                       : MathMax(0.0,(reference_poi-close)/atr));
      return(MathIsValidNumber(sweep_atr) && MathIsValidNumber(reclaim_atr));
     }

   int FindExactLevelAge(const double &values[],const double level,
                         const double point,const int lookback) const
     {
      if(level<=0.0 || point<=0.0 || lookback<2 ||
         ArraySize(values)<lookback+1)
         return(-1);
      for(int index=2; index<=lookback; index++)
         if(MathAbs(values[index]-level)<=point*0.5)
            return(index);
      return(-1);
     }

   bool PriorPoiTouchStats(const double &highs[],const double &lows[],
                           const double poi,const double point,
                           const int lookback,int &latest_age,int &count) const
     {
      if(poi<=0.0 || point<=0.0 || lookback<1 ||
         ArraySize(highs)<lookback+1 || ArraySize(lows)<lookback+1)
         return(false);
      latest_age=-1;
      count=0;
      for(int index=1; index<=lookback; index++)
        {
         if(highs[index]+point*0.5>=poi && lows[index]-point*0.5<=poi)
           {
            if(latest_age<0)
               latest_age=index;
            count++;
           }
        }
      return(latest_age>=1 && count>=1);
     }

   int Export(const string request_file,const string output_file,
              const string data_symbol,const int progress_interval=25)
     {
      if(request_file=="" || output_file=="" || data_symbol=="" ||
         progress_interval<=0 || !SymbolSelect(data_symbol,true) ||
         !m_brain.Initialize())
         return(-1);
      const int input_handle=FileOpen(request_file,
                                      FILE_CSV|FILE_READ|FILE_ANSI,',');
      if(input_handle==INVALID_HANDLE)
        {
         m_brain.Shutdown();
         Print("Past-only trigger-event request file was not found: ",
               request_file);
         return(-1);
        }
      if(!ReadAndValidateHeader(input_handle))
         return(AbortExport(input_handle,INVALID_HANDLE,output_file,
                            "request schema mismatch"));
      if(FileIsExist(output_file) && !FileDelete(output_file))
         return(AbortExport(input_handle,INVALID_HANDLE,output_file,
                            "old output could not be removed"));
      const int output=FileOpen(output_file,FILE_CSV|FILE_WRITE|FILE_ANSI,',');
      if(output==INVALID_HANDLE)
         return(AbortExport(input_handle,output,output_file,
                            "output file could not be opened"));
      FileWrite(output,
                "export_schema_version","request_id","observation_time",
                "symbol","data_symbol","direction","entry_bar_open","context_bar_open",
                "entry_atr","trigger_open","trigger_high","trigger_low",
                "trigger_close","context_open","context_high","context_low",
                "context_close","trigger_range_atr","trigger_body_atr",
                "directional_trigger_body_atr","upper_wick_atr",
                "lower_wick_atr","trigger_close_location",
                "context_body_atr","directional_context_body_atr",
                "context_close_location","trigger_followthrough_atr",
                "sweep_penetration_atr","reclaim_distance_atr",
                "entry_drift_atr","poi_level_age_bars",
                "target_level_age_bars","prior_poi_touch_age_bars",
                "prior_poi_touch_count_64","entry_parity_valid",
                "structure_parity_valid","trigger_parity_valid",
                "history_known_at_valid","deployment_authorized");

      int written=0;
      while(!FileIsEnding(input_handle))
        {
         const string schema=FileReadString(input_handle);
         if(schema=="" && FileIsEnding(input_handle))
            break;
         const string request_id=FileReadString(input_handle);
         const string observation_text=FileReadString(input_handle);
         const string symbol=FileReadString(input_handle);
         const string direction=FileReadString(input_handle);
         const string entry_bar_text=FileReadString(input_handle);
         const string context_bar_text=FileReadString(input_handle);
         const double expected_entry=StringToDouble(FileReadString(input_handle));
         const double reference_poi=StringToDouble(FileReadString(input_handle));
         const double structural_stop=StringToDouble(FileReadString(input_handle));
         const double nearest_target=StringToDouble(FileReadString(input_handle));
         const double expected_sweep=StringToDouble(FileReadString(input_handle));
         const double expected_reclaim=StringToDouble(FileReadString(input_handle));
         const double point_size=StringToDouble(FileReadString(input_handle));
         const int lookback=(int)StringToInteger(FileReadString(input_handle));
         const string deployment=FileReadString(input_handle);
         const datetime observation=StringToTime(observation_text);
         const datetime entry_bar_open=StringToTime(entry_bar_text);
         const datetime context_bar_open=StringToTime(context_bar_text);
         const bool buy=(direction=="TRADE_SETUP_BUY");
         const bool sell=(direction=="TRADE_SETUP_SELL");
         if(schema!="1.0.0" || request_id=="" || symbol!="XAUUSD" ||
            StringFind(data_symbol,symbol)!=0 ||
            deployment!="false" || (!buy && !sell) || lookback!=64 ||
            expected_sweep<=0.0 || expected_reclaim<=0.0 ||
            !ExactTiming(context_bar_open,entry_bar_open,observation) ||
            !ValidGeometry(direction,expected_entry,reference_poi,
                           structural_stop,nearest_target,point_size))
            return(AbortExport(input_handle,output,output_file,
                               "malformed request "+request_id));

         const double broker_point=SymbolInfoDouble(data_symbol,SYMBOL_POINT);
         if(broker_point<=0.0 || MathAbs(broker_point-point_size)>1e-12)
            return(AbortExport(input_handle,output,output_file,
                               "broker point parity mismatch "+request_id));
         if(!EnsureHistory(data_symbol,entry_bar_open,lookback+3))
            return(AbortExport(input_handle,output,output_file,
                               "M5 history unavailable "+request_id));
         const int entry_shift=iBarShift(data_symbol,PERIOD_M5,entry_bar_open,true);
         const int context_shift=iBarShift(data_symbol,PERIOD_M5,context_bar_open,true);
         if(entry_shift<1 || context_shift!=entry_shift+1 ||
            iTime(data_symbol,PERIOD_M5,entry_shift)!=entry_bar_open ||
            iTime(data_symbol,PERIOD_M5,context_shift)!=context_bar_open)
            return(AbortExport(input_handle,output,output_file,
                               "M5 timing unavailable "+request_id));

         CBrainPipelineResult entry_brain=
            m_brain.Think(data_symbol,PERIOD_M5,entry_shift);
         if(!entry_brain.Valid || entry_brain.Analysis.Volatility.ATR<=0.0)
            return(AbortExport(input_handle,output,output_file,
                               "Brain ATR unavailable "+request_id));
         const double atr=entry_brain.Analysis.Volatility.ATR;
         CConfirmedSwingStructureResult structure;
         if(!m_brain.ConfirmedSwingStructure(
               data_symbol,PERIOD_M5,entry_shift,entry_bar_open,observation,structure) ||
            !structure.Valid)
            return(AbortExport(input_handle,output,output_file,
                               "swing structure unavailable "+request_id));
         const double expected_poi=(buy ? structure.LatestSwingLow
                                        : structure.LatestSwingHigh);
         const double expected_target=(buy ? structure.LatestSwingHigh
                                           : structure.LatestSwingLow);
         const bool structure_parity=
            (MathAbs(expected_poi-reference_poi)<=point_size*0.5 &&
             MathAbs(expected_target-nearest_target)<=point_size*0.5);
         if(!structure_parity)
            return(AbortExport(input_handle,output,output_file,
                               "swing structure parity mismatch "+request_id));

         const double trigger_open=iOpen(data_symbol,PERIOD_M5,entry_shift);
         const double trigger_high=iHigh(data_symbol,PERIOD_M5,entry_shift);
         const double trigger_low=iLow(data_symbol,PERIOD_M5,entry_shift);
         const double trigger_close=iClose(data_symbol,PERIOD_M5,entry_shift);
         const double context_open=iOpen(data_symbol,PERIOD_M5,context_shift);
         const double context_high=iHigh(data_symbol,PERIOD_M5,context_shift);
         const double context_low=iLow(data_symbol,PERIOD_M5,context_shift);
         const double context_close=iClose(data_symbol,PERIOD_M5,context_shift);
         const bool entry_parity=
            (MathAbs(trigger_close-expected_entry)<=point_size*0.5);
         if(!entry_parity)
            return(AbortExport(input_handle,output,output_file,
                               "Entry parity mismatch "+request_id));

         double trigger_range=0.0,trigger_body=0.0,directional_trigger=0.0;
         double upper_wick=0.0,lower_wick=0.0,trigger_close_location=0.0;
         double context_range=0.0,context_body=0.0,directional_context=0.0;
         double context_upper=0.0,context_lower=0.0,context_close_location=0.0;
         if(!CalculateBarShape(direction,trigger_open,trigger_high,trigger_low,
                               trigger_close,atr,trigger_range,trigger_body,
                               directional_trigger,upper_wick,lower_wick,
                               trigger_close_location) ||
            !CalculateBarShape(direction,context_open,context_high,context_low,
                               context_close,atr,context_range,context_body,
                               directional_context,context_upper,context_lower,
                               context_close_location) || directional_trigger<=0.0)
            return(AbortExport(input_handle,output,output_file,
                               "bar shape invalid "+request_id));

         double sweep=0.0,reclaim=0.0;
         if(!DirectionalEvidence(direction,trigger_high,trigger_low,
                                 trigger_close,reference_poi,atr,sweep,reclaim))
            return(AbortExport(input_handle,output,output_file,
                               "trigger evidence invalid "+request_id));
         const bool trigger_parity=
            (MathAbs(sweep-expected_sweep)<=1e-6 &&
             MathAbs(reclaim-expected_reclaim)<=1e-6);
         if(!trigger_parity)
            return(AbortExport(input_handle,output,output_file,
                               "trigger evidence parity mismatch "+request_id));

         double highs[],lows[];
         if(!LoadKnownBars(data_symbol,entry_shift,lookback,highs,lows))
            return(AbortExport(input_handle,output,output_file,
                               "known-bar load failed "+request_id));
         int poi_age=-1;
         int target_age=-1;
         if(buy)
           {
            poi_age=FindExactLevelAge(lows,reference_poi,point_size,lookback);
            target_age=FindExactLevelAge(highs,nearest_target,point_size,lookback);
           }
         else
           {
            poi_age=FindExactLevelAge(highs,reference_poi,point_size,lookback);
            target_age=FindExactLevelAge(lows,nearest_target,point_size,lookback);
           }
         int prior_touch_age=-1;
         int prior_touch_count=0;
         if(poi_age<2 || target_age<2 ||
            !PriorPoiTouchStats(highs,lows,reference_poi,point_size,lookback,
                                prior_touch_age,prior_touch_count))
            return(AbortExport(input_handle,output,output_file,
                               "structural age unavailable "+request_id));

         const double followthrough=(buy ? trigger_close-context_close
                                         : context_close-trigger_close)/atr;
         const double entry_drift=MathAbs(expected_entry-trigger_close)/atr;
         if(!MathIsValidNumber(followthrough) ||
            !MathIsValidNumber(entry_drift))
            return(AbortExport(input_handle,output,output_file,
                               "derived trigger value invalid "+request_id));

         if(FileWrite(output,"1.1.0",request_id,observation_text,symbol,
                      data_symbol,direction,entry_bar_text,context_bar_text,atr,
                      trigger_open,trigger_high,trigger_low,trigger_close,
                      context_open,context_high,context_low,context_close,
                      trigger_range,trigger_body,directional_trigger,upper_wick,
                      lower_wick,trigger_close_location,context_body,
                      directional_context,context_close_location,followthrough,
                      sweep,reclaim,entry_drift,poi_age,target_age,
                      prior_touch_age,prior_touch_count,"true","true","true",
                      "true","false")==0)
            return(AbortExport(input_handle,output,output_file,
                               "output write failed "+request_id));
         written++;
         if(written%progress_interval==0)
           {
            FileFlush(output);
            Print("Past-only trigger-event export progress: ",written,
                  " requests");
           }
        }
      FileFlush(output);
      FileClose(input_handle);
      FileClose(output);
      m_brain.Shutdown();
      return(written);
     }
  };

#endif
