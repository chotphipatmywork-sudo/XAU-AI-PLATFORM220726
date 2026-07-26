//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : OutcomeFreeM5PathExporter.mqh                           |
//| Layer   : Core / AI / Learning / Offline Research                |
//| Version : 1.0.0                                                  |
//| Purpose : Export outcome-free IMP-100 causal closed-M5 paths     |
//+------------------------------------------------------------------+
#ifndef CORE_AI_OUTCOMEFREEM5PATHEXPORTER_MQH
#define CORE_AI_OUTCOMEFREEM5PATHEXPORTER_MQH
class COutcomeFreeM5PathExporter
  {
private:
   bool ContainsRequestId(string &request_ids[],const string request_id) const
     {
      for(int index=0; index<ArraySize(request_ids); index++)
         if(request_ids[index]==request_id) return(true);
      return(false);
     }
   bool ReadAndValidateHeader(const int handle) const
     {
      const string expected[]={
         "request_schema_version","request_id","base_opportunity_id",
         "source_record_id","arm_id","observation_time","symbol",
         "direction","entry_price","stop_identity","stop_price",
         "target_identity","target_price","minimum_rr","geometry_eligible",
         "common_support","train_cutoff_compliant","source_sha256",
         "deployment_authorized"
      };
      for(int index=0; index<ArraySize(expected); index++)
         if(FileReadString(handle)!=expected[index]) return(false);
      return(true);
     }
   int AbortExport(const int input_handle,const int output_handle,
                   const string output_file,const string reason) const
     {
      if(input_handle!=INVALID_HANDLE) FileClose(input_handle);
      if(output_handle!=INVALID_HANDLE) FileClose(output_handle);
      if(FileIsExist(output_file,true)) FileDelete(output_file,true);
      Print("IMP-100 outcome-free M5 export failed closed: ",reason);
      return(-1);
     }
   bool ValidGeometry(const string direction,const double entry,
                      const double stop,const double target,
                      const double minimum_rr) const
     {
      const bool buy=(direction=="TRADE_SETUP_BUY");
      const bool sell=(direction=="TRADE_SETUP_SELL");
      if((!buy && !sell) || entry<=0.0 || stop<=0.0 || target<=0.0 ||
         minimum_rr<2.0-1e-9) return(false);
      return((buy && stop<entry && entry<target) ||
             (sell && target<entry && entry<stop));
     }
   bool LoadClosedM5Rates(const string symbol,const datetime observation,
                          const datetime train_cutoff,const int maximum_bars,
                          MqlRates &rates[]) const
     {
      ArrayResize(rates,0);
      ArraySetAsSeries(rates,false);
      const datetime fourteen_days=observation+14*24*60*60;
      const datetime search_end=(train_cutoff<fourteen_days ?
                                 train_cutoff : fourteen_days);
      if(!ValidWindow(observation,train_cutoff,maximum_bars) ||
         search_end<=observation) return(false);
      int copied=-1;
      int last_error=0;
      for(int attempt=0; attempt<40; attempt++)
        {
         ResetLastError();
         copied=CopyRates(symbol,PERIOD_M5,observation,search_end-1,rates);
         last_error=GetLastError();
         if(copied>=maximum_bars && rates[0].time==observation) break;
         Sleep(250);
        }
      if(copied<maximum_bars || rates[0].time!=observation)
        {
         Print("IMP-100 closed M5 history unavailable: symbol=",symbol,
               " observation=",TimeToString(observation)," copied=",copied,
               " required=",maximum_bars," error=",last_error);
         return(false);
        }
      ArrayResize(rates,maximum_bars);
      datetime previous=0;
      const int seconds=PeriodSeconds(PERIOD_M5);
      for(int index=0; index<maximum_bars; index++)
        {
         const datetime bar_open=rates[index].time;
         if(bar_open<observation || bar_open+seconds>train_cutoff ||
            bar_open%seconds!=0 ||
            (previous>0 &&
             (bar_open<=previous || (bar_open-previous)%seconds!=0)) ||
            rates[index].open<=0.0 || rates[index].high<=0.0 ||
            rates[index].low<=0.0 || rates[index].close<=0.0 ||
            rates[index].high<rates[index].low ||
            rates[index].high<MathMax(rates[index].open,rates[index].close) ||
            rates[index].low>MathMin(rates[index].open,rates[index].close))
            return(false);
         previous=bar_open;
        }
      return(true);
     }
public:
   bool ValidWindow(const datetime observation,const datetime train_cutoff,
                    const int maximum_path_m5_bars) const
     {
      const int seconds=PeriodSeconds(PERIOD_M5);
      return(observation>0 && train_cutoff>observation && seconds>0 &&
             observation%seconds==0 && maximum_path_m5_bars>=1 &&
             maximum_path_m5_bars<=192);
     }
   bool BarIsCausallyClosed(const datetime bar_open,
                            const datetime observation,
                            const datetime train_cutoff) const
     {
      return(bar_open>=observation &&
             bar_open+PeriodSeconds(PERIOD_M5)<=train_cutoff);
     }
   int Export(const string request_file,const string output_file,
              const datetime train_cutoff,
              const int maximum_path_m5_bars=192,
              const int progress_interval=25)
     {
      if(request_file=="" || output_file=="" || progress_interval<=0 ||
         train_cutoff<=0 || maximum_path_m5_bars<=0) return(-1);
      const int input_handle=FileOpen(
         request_file,FILE_CSV|FILE_READ|FILE_ANSI|FILE_COMMON,',');
      if(input_handle==INVALID_HANDLE)
        {
         Print("IMP-100 outcome-free request file was not found: ",request_file);
         return(-1);
        }
      if(!ReadAndValidateHeader(input_handle))
         return(AbortExport(input_handle,INVALID_HANDLE,output_file,
                            "request schema mismatch"));
      if(FileIsExist(output_file,true) && !FileDelete(output_file,true))
         return(AbortExport(input_handle,INVALID_HANDLE,output_file,
                            "old output could not be removed"));
      const int output=FileOpen(
         output_file,FILE_CSV|FILE_WRITE|FILE_ANSI|FILE_COMMON,',');
      if(output==INVALID_HANDLE)
         return(AbortExport(input_handle,output,output_file,
                            "output file could not be opened"));
      FileWrite(output,"export_schema_version","request_id",
                "base_opportunity_id","source_record_id","arm_id",
                "observation_time","path_end_exclusive","symbol",
                "direction","sequence","bar_open","open","high","low",
                "close","tick_volume","spread","real_volume",
                "entry_price","stop_identity","stop_price",
                "target_identity","target_price","minimum_rr",
                "common_support","source_sha256","closed_m5_only",
                "deployment_authorized");
      int requests=0;
      int path_rows=0;
      datetime previous_observation=0;
      string request_ids[];
      while(!FileIsEnding(input_handle))
        {
         const string schema=FileReadString(input_handle);
         if(schema=="" && FileIsEnding(input_handle)) break;
         const string request_id=FileReadString(input_handle);
         const string base_id=FileReadString(input_handle);
         const string source_record_id=FileReadString(input_handle);
         const string arm_id=FileReadString(input_handle);
         const string observation_text=FileReadString(input_handle);
         const string symbol=FileReadString(input_handle);
         const string direction=FileReadString(input_handle);
         const double entry=StringToDouble(FileReadString(input_handle));
         const string stop_identity=FileReadString(input_handle);
         const double stop=StringToDouble(FileReadString(input_handle));
         const string target_identity=FileReadString(input_handle);
         const double target=StringToDouble(FileReadString(input_handle));
         const double minimum_rr=StringToDouble(FileReadString(input_handle));
         const string geometry_eligible=FileReadString(input_handle);
         const string common_support=FileReadString(input_handle);
         const string cutoff_compliant=FileReadString(input_handle);
         const string source_sha256=FileReadString(input_handle);
         const string deployment=FileReadString(input_handle);
         const datetime observation=StringToTime(observation_text);
         if(schema!="1.0.0" || request_id=="" || base_id=="" ||
            source_record_id=="" || arm_id=="" || symbol!="XAUUSD" ||
            stop_identity=="" || target_identity=="" ||
            geometry_eligible!="true" ||
            (common_support!="true" && common_support!="false") ||
            cutoff_compliant!="true" || source_sha256=="" ||
            deployment!="false" ||
            (previous_observation>0 && observation<previous_observation) ||
            ContainsRequestId(request_ids,request_id) ||
            !ValidWindow(observation,train_cutoff,maximum_path_m5_bars) ||
            !ValidGeometry(direction,entry,stop,target,minimum_rr))
            return(AbortExport(input_handle,output,output_file,
                               "malformed or unordered request "+request_id));
         MqlRates rates[];
         if(!LoadClosedM5Rates(symbol,observation,train_cutoff,
                               maximum_path_m5_bars,rates))
            return(AbortExport(input_handle,output,output_file,
                               "M5 path unavailable "+request_id));
         const datetime path_end=rates[maximum_path_m5_bars-1].time+
                                  PeriodSeconds(PERIOD_M5);
         const string path_end_text=TimeToString(path_end,TIME_DATE|TIME_MINUTES);
         for(int index=0; index<maximum_path_m5_bars; index++)
           {
            if(FileWrite(output,"1.0.0",request_id,base_id,source_record_id,
                         arm_id,observation_text,path_end_text,symbol,direction,
                         index+1,TimeToString(rates[index].time,
                                              TIME_DATE|TIME_MINUTES),
                         rates[index].open,rates[index].high,rates[index].low,
                         rates[index].close,rates[index].tick_volume,
                         rates[index].spread,rates[index].real_volume,entry,
                         stop_identity,stop,target_identity,target,minimum_rr,
                         common_support,source_sha256,"true","false")==0)
               return(AbortExport(input_handle,output,output_file,
                                  "output write failed "+request_id));
            path_rows++;
           }
         const int request_index=ArraySize(request_ids);
         ArrayResize(request_ids,request_index+1);
         request_ids[request_index]=request_id;
         previous_observation=observation;
         requests++;
         if(requests%progress_interval==0)
           {
            FileFlush(output);
            Print("IMP-100 outcome-free M5 export progress: ",requests,
                  " requests, ",path_rows," path rows");
           }
        }
      FileFlush(output);
      FileClose(input_handle);
      FileClose(output);
      Print("IMP-100 outcome-free M5 path rows written: ",path_rows);
      return(requests);
     }
  };
#endif