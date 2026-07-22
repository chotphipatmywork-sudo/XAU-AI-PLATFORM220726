//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : IModule.mqh                                            |
//| Layer   : Interfaces                                             |
//+------------------------------------------------------------------+

#ifndef CORE_INTERFACES_IMODULE_MQH
#define CORE_INTERFACES_IMODULE_MQH

class IModule
{
public:
    virtual bool Initialize() = 0;

    virtual bool Update() = 0;

    virtual void Shutdown() = 0;

    virtual ~IModule() {}
};

#endif