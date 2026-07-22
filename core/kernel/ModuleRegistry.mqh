//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : ModuleRegistry.mqh                                     |
//| Layer   : Kernel                                                 |
//+------------------------------------------------------------------+

#ifndef CORE_KERNEL_MODULEREGISTRY_MQH
#define CORE_KERNEL_MODULEREGISTRY_MQH

#include "../interfaces/IModule.mqh"

class CModuleRegistry
{
private:
    IModule *m_modules[64];

    int m_count;

public:
    CModuleRegistry()
    {
        m_count = 0;
    }

    bool Register(IModule *module)
    {
        if (m_count >= 64)
            return false;

        m_modules[m_count] = module;
        m_count++;

        return true;
    }

    void ShutdownAll()
    {
        for (int i = 0; i < m_count; i++)
        {
            if (m_modules[i] != NULL)
                m_modules[i].Shutdown();
        }
    }
};

#endif