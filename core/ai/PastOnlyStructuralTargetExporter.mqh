//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : PastOnlyStructuralTargetExporter.mqh                   |
//| Layer   : Core / AI / Learning / Offline Research                |
//| Version : 1.0.0                                                  |
//| Purpose : Export past-only M5/M15 confirmed Target ladders       |
//+------------------------------------------------------------------+

#ifndef CORE_AI_PASTONLYSTRUCTURALTARGETEXPORTER_MQH
#define CORE_AI_PASTONLYSTRUCTURALTARGETEXPORTER_MQH

class CPastOnlyStructuralTargetExporter
  {
private:
   int m_left_bars;
   int m_right_bars;
   int m_lookback;
   int m_max_targets;

   bool IsPivotHigh(const double &highs[],const int index) const
     {
      const double value=highs[index];
      for(int offset=1; offset<=m_right_bars; offset++)
         if(value<=highs[index-offset])
            return(false);
      for(int offset=1; offset<=m_left_bars; offset++)
         if(value<=highs[index+offset])
            return(false);
      return(true);
     }

   bool IsPivotLow(const double &lows[],const int index) const
     {
      const double value=lows[index];
      for(int offset=1; offset<=m_right_bars; offset++)
         if(value>=lows[index-offset])
            return(false);
      for(int offset=1; offset<=m_left_bars; offset++)
         if(value>=lows[index+offset])
            return(false);
      return(true);
     }

   bool AddUnique(const double value,const double point,double &values[]) const
     {
      const int size=ArraySize(values);
      for(int index=0; index<size; index++)
         if(MathAbs(values[index]-value)<=point*0.5)
            return(true);
      if(ArrayResize(values,size+1)!=size+1)
         return(false);
      values[size]=value;
      return(true);
     }

   void SortSpatial(double &values[],const bool buy) const
     {
      const int size=ArraySize(values);
      for(int left=0; left<size-1; left++)
         for(int right=left+1; right<size; right++)
           {
            const bool swap=(buy ? values[right]<values[left]
                                 : values[right]>values[left]);
            if(swap)
              {
               const double temporary=values[left];
               values[left]=values[right];
               values[right]=temporary;
              }
           }
     }

   bool EnsureHistory(const string symbol,const ENUM_TIMEFRAMES timeframe,
                      const datetime latest_closed_bar_open) const
     {
      MqlRates rates[];
      int copied=-1;
      int last_error=0;
      for(int attempt=0; attempt<40; attempt++)
        {
         ResetLastError();
         copied=CopyRates(symbol,timeframe,latest_closed_bar_open,
                          RequiredBars(),rates);
         last_error=GetLastError();
         if(copied>=RequiredBars())
            return(true);
         Sleep(250);
        }
      Print("Past-only Target history prefetch failed: symbol=",symbol,
            " timeframe=",EnumToString(timeframe),
            " latest=",TimeToString(latest_closed_bar_open),
            " copied=",copied," error=",last_error,
            " terminal_max_bars=",TerminalInfoInteger(TERMINAL_MAXBARS));
      return(false);
     }

   bool LoadRates(const string symbol,const ENUM_TIMEFRAMES timeframe,
                  const datetime latest_closed_bar_open,
                  const datetime observation,double &highs[],
                  double &lows[]) const
     {
      const int seconds=PeriodSeconds(timeframe);
      if(symbol=="" || seconds<=0 || latest_closed_bar_open<=0 ||
         observation<=0 || latest_closed_bar_open+seconds>observation)
         return(false);
      if(!EnsureHistory(symbol,timeframe,latest_closed_bar_open))
         return(false);
      const int shift=iBarShift(symbol,timeframe,latest_closed_bar_open,true);
      if(shift<0 || iTime(symbol,timeframe,shift)!=latest_closed_bar_open)
         return(false);
      const int count=RequiredBars();
      ArrayResize(highs,count);
      ArrayResize(lows,count);
      for(int index=0; index<count; index++)
        {
         const int source_shift=shift+index;
         const datetime bar_open=iTime(symbol,timeframe,source_shift);
         highs[index]=iHigh(symbol,timeframe,source_shift);
         lows[index]=iLow(symbol,timeframe,source_shift);
         if(bar_open<=0 || bar_open+seconds>observation ||
            highs[index]<=0.0 || lows[index]<=0.0 ||
            highs[index]<lows[index])
            return(false);
        }
      return(true);
     }

   bool ParseBoolean(const string text,bool &value) const
     {
      if(text=="true")
        {
         value=true;
         return(true);
        }
      if(text=="false")
        {
         value=false;
         return(true);
        }
      return(false);
     }

   bool ReadAndValidateHeader(const int handle) const
     {
      const string expected[]={
         "request_schema_version","request_id","source","observation_time",
         "symbol","direction","entry_bar_open","expected_entry",
         "entry_known","structural_stop","current_target",
         "estimated_cost_points","cost_known","minimum_rr"
      };
      for(int index=0; index<ArraySize(expected); index++)
         if(FileReadString(handle)!=expected[index])
            return(false);
      return(true);
     }

   double Slot(const double &values[],const int index) const
     {
      return(index<ArraySize(values) ? values[index] : 0.0);
     }

   int AbortExport(const int input_handle,const int output_handle,
                   const string output_file,const string reason) const
     {
      if(input_handle!=INVALID_HANDLE)
         FileClose(input_handle);
      if(output_handle!=INVALID_HANDLE)
         FileClose(output_handle);
      if(FileIsExist(output_file))
         FileDelete(output_file);
      Print("Past-only structural Target export failed closed: ",reason);
      return(-1);
     }

public:
   CPastOnlyStructuralTargetExporter(void)
     {
      m_left_bars=2;
      m_right_bars=2;
      m_lookback=64;
      m_max_targets=3;
     }

   int RequiredBars(void) const
     {
      return(m_lookback+m_left_bars+1);
     }

   bool ExactTriggerTiming(const datetime entry_bar_open,
                           const datetime observation) const
     {
      return(entry_bar_open>0 && observation>0 &&
             entry_bar_open+PeriodSeconds(PERIOD_M5)==observation);
     }

   int BuildTargetLadder(const double entry,const bool buy,
                         const double &highs[],const double &lows[],
                         const double point,double &targets[]) const
     {
      ArrayResize(targets,0);
      const int size=ArraySize(highs);
      if(entry<=0.0 || point<=0.0 || size!=ArraySize(lows) ||
         size<RequiredBars())
         return(-1);
      const int final_index=MathMin(m_lookback,size-m_left_bars-1);
      for(int index=m_right_bars; index<=final_index; index++)
        {
         double candidate=0.0;
         if(buy && IsPivotHigh(highs,index) && highs[index]>entry+point*0.5)
            candidate=highs[index];
         else if(!buy && IsPivotLow(lows,index) && lows[index]<entry-point*0.5)
            candidate=lows[index];
         if(candidate>0.0 && !AddUnique(candidate,point,targets))
            return(-1);
        }
      SortSpatial(targets,buy);
      if(ArraySize(targets)>m_max_targets)
         ArrayResize(targets,m_max_targets);
      return(ArraySize(targets));
     }

   int Export(const string request_file,const string output_file,
              const int progress_interval=100)
     {
      if(request_file=="" || output_file=="" || progress_interval<=0)
         return(-1);
      const int input_handle=FileOpen(request_file,
                                     FILE_CSV|FILE_READ|FILE_ANSI,',');
      if(input_handle==INVALID_HANDLE)
        {
         Print("Past-only structural Target request file was not found: ",
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
                "export_schema_version","request_id","source",
                "observation_time","symbol","direction","entry_bar_open",
                "entry_price","expected_entry","entry_parity_required",
                "entry_parity_valid","structural_stop","current_target",
                "estimated_cost_points","cost_known","minimum_rr",
                "m5_target_1","m5_target_2","m5_target_3","m5_target_count",
                "m15_target_1","m15_target_2","m15_target_3","m15_target_count",
                "known_time_valid","deployment_authorized");

      int written=0;
      while(!FileIsEnding(input_handle))
        {
         const string schema=FileReadString(input_handle);
         if(schema=="" && FileIsEnding(input_handle))
            break;
         const string request_id=FileReadString(input_handle);
         const string source=FileReadString(input_handle);
         const string observation_text=FileReadString(input_handle);
         const string symbol=FileReadString(input_handle);
         const string direction=FileReadString(input_handle);
         const string entry_bar_text=FileReadString(input_handle);
         const double expected_entry=StringToDouble(FileReadString(input_handle));
         const string entry_known_text=FileReadString(input_handle);
         const double structural_stop=StringToDouble(FileReadString(input_handle));
         const double current_target=StringToDouble(FileReadString(input_handle));
         const double cost_points=StringToDouble(FileReadString(input_handle));
         const string cost_known_text=FileReadString(input_handle);
         const double minimum_rr=StringToDouble(FileReadString(input_handle));

         bool entry_known=false;
         bool cost_known=false;
         const datetime observation=StringToTime(observation_text);
         const datetime entry_bar_open=StringToTime(entry_bar_text);
         const bool buy=(direction=="TRADE_SETUP_BUY");
         const bool sell=(direction=="TRADE_SETUP_SELL");
         if(schema!="1.0.0" || request_id=="" || source=="" || symbol=="" ||
            observation<=0 || entry_bar_open<=0 || (!buy && !sell) ||
            !ParseBoolean(entry_known_text,entry_known) ||
            !ParseBoolean(cost_known_text,cost_known) ||
            structural_stop<=0.0 || current_target<=0.0 ||
            cost_points<0.0 || minimum_rr<2.0 ||
            (entry_known && expected_entry<=0.0) ||
            (!entry_known && expected_entry!=0.0) ||
            (cost_known && !entry_known) ||
            (!cost_known && cost_points!=0.0) ||
            !ExactTriggerTiming(entry_bar_open,observation))
            return(AbortExport(input_handle,output,output_file,
                               "malformed request "+request_id));

         if(!EnsureHistory(symbol,PERIOD_M5,entry_bar_open))
            return(AbortExport(input_handle,output,output_file,
                               "M5 trigger history unavailable "+request_id));
         const int entry_shift=iBarShift(symbol,PERIOD_M5,entry_bar_open,true);
         if(entry_shift<0 || iTime(symbol,PERIOD_M5,entry_shift)!=entry_bar_open)
            return(AbortExport(input_handle,output,output_file,
                               "missing M5 trigger bar "+request_id));
         const double entry=iClose(symbol,PERIOD_M5,entry_shift);
         const double point=SymbolInfoDouble(symbol,SYMBOL_POINT);
         if(entry<=0.0 || point<=0.0)
            return(AbortExport(input_handle,output,output_file,
                               "invalid Entry or point size "+request_id));
         const bool parity_valid=(!entry_known ||
                                  MathAbs(entry-expected_entry)<=point*0.5);
         if(!parity_valid)
            return(AbortExport(input_handle,output,output_file,
                               "Entry parity mismatch "+request_id));

         double m5_highs[];
         double m5_lows[];
         double m15_highs[];
         double m15_lows[];
         if(!LoadRates(symbol,PERIOD_M5,entry_bar_open,observation,
                       m5_highs,m5_lows) ||
            !LoadRates(symbol,PERIOD_M15,
                       observation-PeriodSeconds(PERIOD_M15),observation,
                       m15_highs,m15_lows))
            return(AbortExport(input_handle,output,output_file,
                               "past-only history unavailable "+request_id));
         double m5_targets[];
         double m15_targets[];
         const int m5_count=BuildTargetLadder(entry,buy,m5_highs,m5_lows,
                                              point,m5_targets);
         const int m15_count=BuildTargetLadder(entry,buy,m15_highs,m15_lows,
                                               point,m15_targets);
         if(m5_count<0 || m15_count<0)
            return(AbortExport(input_handle,output,output_file,
                               "Target ladder failed "+request_id));

         if(FileWrite(output,"1.0.0",request_id,source,observation_text,
                      symbol,direction,entry_bar_text,entry,expected_entry,
                      (entry_known ? "true" : "false"),"true",
                      structural_stop,current_target,cost_points,
                      (cost_known ? "true" : "false"),minimum_rr,
                      Slot(m5_targets,0),Slot(m5_targets,1),Slot(m5_targets,2),
                      m5_count,Slot(m15_targets,0),Slot(m15_targets,1),
                      Slot(m15_targets,2),m15_count,"true","false")==0)
            return(AbortExport(input_handle,output,output_file,
                               "output write failed "+request_id));
         written++;
         if(written%progress_interval==0)
           {
            FileFlush(output);
            Print("Past-only structural Target export progress: ",written,
                  " requests");
           }
        }
      FileFlush(output);
      FileClose(input_handle);
      FileClose(output);
      return(written);
     }
  };

#endif
