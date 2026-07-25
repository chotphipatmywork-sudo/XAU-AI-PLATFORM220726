//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : PastOnlyLifecyclePathExporter.mqh                      |
//| Layer   : Core / AI / Learning / Offline Research                |
//| Version : 1.1.0                                                  |
//| Purpose : Export mature Effective-Train M5 lifecycle paths       |
//+------------------------------------------------------------------+

#ifndef CORE_AI_PASTONLYLIFECYCLEPATHEXPORTER_MQH
#define CORE_AI_PASTONLYLIFECYCLEPATHEXPORTER_MQH

class CPastOnlyLifecyclePathExporter
  {
private:
   bool ReadAndValidateHeader(const int handle) const
     {
      const string expected[]={
         "request_schema_version","request_id","observation_time",
         "outcome_known_at","symbol","direction","entry","initial_stop",
         "target","estimated_cost_points","point_size","plan_rr",
         "baseline_outcome","maximum_path_m5_bars","deployment_authorized"
      };
      for(int index=0; index<ArraySize(expected); index++)
         if(FileReadString(handle)!=expected[index])
            return(false);
      return(true);
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
      Print("Past-only lifecycle M5 export failed closed: ",reason);
      return(-1);
     }

   bool LoadM5Rates(const string symbol,const datetime observation,
                    const datetime known_at,MqlRates &rates[]) const
     {
      ArrayResize(rates,0);
      ArraySetAsSeries(rates,false);
      int copied=-1;
      int last_error=0;
      for(int attempt=0; attempt<40; attempt++)
        {
         ResetLastError();
         copied=CopyRates(symbol,PERIOD_M5,observation,known_at-1,rates);
         last_error=GetLastError();
         if(copied>0 && rates[0].time==observation &&
            rates[copied-1].time+PeriodSeconds(PERIOD_M5)==known_at)
            break;
         Sleep(250);
        }
      if(copied<=0 || rates[0].time!=observation ||
         rates[copied-1].time+PeriodSeconds(PERIOD_M5)!=known_at)
        {
         Print("Past-only lifecycle M5 history unavailable: symbol=",symbol,
               " observation=",TimeToString(observation),
               " known_at=",TimeToString(known_at)," copied=",copied,
               " error=",last_error,
               " terminal_max_bars=",TerminalInfoInteger(TERMINAL_MAXBARS));
         return(false);
        }
      datetime previous=0;
      for(int index=0; index<copied; index++)
        {
         if(!BarWithinWindow(rates[index].time,observation,known_at) ||
            (previous>0 && rates[index].time<=previous) ||
            rates[index].open<=0.0 || rates[index].high<=0.0 ||
            rates[index].low<=0.0 || rates[index].close<=0.0 ||
            rates[index].high<rates[index].low ||
            rates[index].high<MathMax(rates[index].open,rates[index].close) ||
            rates[index].low>MathMin(rates[index].open,rates[index].close))
            return(false);
         previous=rates[index].time;
        }
      return(true);
     }

public:
   bool ValidWindow(const datetime observation,const datetime known_at,
                    const int maximum_path_m5_bars) const
     {
      const int seconds=PeriodSeconds(PERIOD_M5);
      return(observation>0 && known_at>observation && seconds>0 &&
             (known_at-observation)%seconds==0 &&
             maximum_path_m5_bars>=1 && maximum_path_m5_bars<=192);
     }

   bool BarWithinWindow(const datetime bar_open,const datetime observation,
                        const datetime known_at) const
     {
      return(bar_open>=observation &&
             bar_open+PeriodSeconds(PERIOD_M5)<=known_at);
     }

   bool ValidGeometry(const string direction,const double entry,
                      const double initial_stop,const double target,
                      const double estimated_cost_points,
                      const double point_size,const double plan_rr) const
     {
      const bool buy=(direction=="TRADE_SETUP_BUY");
      const bool sell=(direction=="TRADE_SETUP_SELL");
      if((!buy && !sell) || entry<=0.0 || initial_stop<=0.0 || target<=0.0 ||
         estimated_cost_points<0.0 || point_size<=0.0 || plan_rr<2.0-1e-9)
         return(false);
      if((buy && !(initial_stop<entry && entry<target)) ||
         (sell && !(target<entry && entry<initial_stop)))
         return(false);
      const double cost=estimated_cost_points*point_size;
      const double risk=MathAbs(entry-initial_stop);
      const double reward=MathAbs(target-entry);
      if(risk<=0.0 || reward<=cost)
         return(false);
      const double calculated=(reward-cost)/(risk+cost);
      return(MathAbs(calculated-plan_rr)<=1e-6);
     }

   int Export(const string request_file,const string output_file,
              const int progress_interval=25)
     {
      if(request_file=="" || output_file=="" || progress_interval<=0)
         return(-1);
      const int input_handle=FileOpen(request_file,
                                      FILE_CSV|FILE_READ|FILE_ANSI,',');
      if(input_handle==INVALID_HANDLE)
        {
         Print("Past-only lifecycle request file was not found: ",request_file);
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
                "outcome_known_at","symbol","direction","sequence",
                "bar_open","open","high","low","close","tick_volume",
                "spread","real_volume","entry","initial_stop","target",
                "estimated_cost_points","point_size","plan_rr",
                "baseline_outcome","path_within_mature_window",
                "deployment_authorized");

      int requests=0;
      int path_rows=0;
      while(!FileIsEnding(input_handle))
        {
         const string schema=FileReadString(input_handle);
         if(schema=="" && FileIsEnding(input_handle))
            break;
         const string request_id=FileReadString(input_handle);
         const string observation_text=FileReadString(input_handle);
         const string known_at_text=FileReadString(input_handle);
         const string symbol=FileReadString(input_handle);
         const string direction=FileReadString(input_handle);
         const double entry=StringToDouble(FileReadString(input_handle));
         const double initial_stop=StringToDouble(FileReadString(input_handle));
         const double target=StringToDouble(FileReadString(input_handle));
         const double cost_points=StringToDouble(FileReadString(input_handle));
         const double point_size=StringToDouble(FileReadString(input_handle));
         const double plan_rr=StringToDouble(FileReadString(input_handle));
         const string baseline_outcome=FileReadString(input_handle);
         const int maximum_bars=(int)StringToInteger(
            FileReadString(input_handle));
         const string deployment=FileReadString(input_handle);
         const datetime observation=StringToTime(observation_text);
         const datetime known_at=StringToTime(known_at_text);
         if(schema!="1.1.0" || request_id=="" || symbol!="XAUUSD" ||
            deployment!="false" ||
            (baseline_outcome!="TARGET_FIRST" &&
             baseline_outcome!="STOP_FIRST") ||
            !ValidWindow(observation,known_at,maximum_bars) ||
            !ValidGeometry(direction,entry,initial_stop,target,cost_points,
                           point_size,plan_rr))
            return(AbortExport(input_handle,output,output_file,
                               "malformed request "+request_id));

         MqlRates rates[];
         if(!LoadM5Rates(symbol,observation,known_at,rates))
            return(AbortExport(input_handle,output,output_file,
                               "M5 path unavailable "+request_id));
         const int count=ArraySize(rates);
         if(count<=0 || count>maximum_bars)
            return(AbortExport(input_handle,output,output_file,
                               "M5 path count invalid "+request_id+
                               " count="+IntegerToString(count)+
                               " ceiling="+IntegerToString(maximum_bars)));
         for(int index=0; index<count; index++)
           {
            if(FileWrite(output,"1.0.0",request_id,observation_text,
                         known_at_text,symbol,direction,index+1,
                         TimeToString(rates[index].time,TIME_DATE|TIME_MINUTES),
                         rates[index].open,rates[index].high,rates[index].low,
                         rates[index].close,rates[index].tick_volume,
                         rates[index].spread,rates[index].real_volume,entry,
                         initial_stop,target,cost_points,point_size,plan_rr,
                         baseline_outcome,"true","false")==0)
               return(AbortExport(input_handle,output,output_file,
                                  "output write failed "+request_id));
            path_rows++;
           }
         requests++;
         if(requests%progress_interval==0)
           {
            FileFlush(output);
            Print("Past-only lifecycle M5 export progress: ",requests,
                  " requests, ",path_rows," path rows");
           }
        }
      FileFlush(output);
      FileClose(input_handle);
      FileClose(output);
      Print("Past-only lifecycle M5 path rows written: ",path_rows);
      return(requests);
     }
  };

#endif
