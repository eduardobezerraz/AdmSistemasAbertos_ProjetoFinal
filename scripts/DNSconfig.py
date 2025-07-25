import subprocess
import re

def main():
    # Interfaces a ignorar
    ignored = ["virtualbox", "vmware", "hyper-v", "loopback", "vpn", "bluetooth", "tunneling"]
    ignore_pattern = "|".join(ignored)
    
    # Obter interfaces de rede
    try:
        # Executa o comando para listar interfaces
        result = subprocess.run(
            ['netsh', 'interface', 'show', 'interface'], 
            capture_output=True, 
            text=True,
            check=True
        )
        
        # Processa a saída para encontrar a primeira interface Ethernet ativa
        interfaces = []
        for line in result.stdout.split('\n'):
            if "Conectado" in line and "Ethernet" in line:
                parts = re.split(r'\s{2,}', line.strip())
                if len(parts) >= 4:
                    interface_name = parts[-1]
                    interface_desc = parts[-2]
                    
                    # Verifica se não é uma interface ignorada
                    if not re.search(ignore_pattern, interface_desc, re.IGNORECASE):
                        interfaces.append(interface_name)
        
        if not interfaces:
            print("Erro: Nenhuma interface de rede cabeada real ativa foi encontrada.")
            exit(1)
            
        interface_name = interfaces[0]
        print(f"Interface selecionada: {interface_name}")
        
        # Obter endereço IP da interface
        ip_result = subprocess.run(
            ['netsh', 'interface', 'ipv4', 'show', 'addresses', f'name="{interface_name}"'],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Extrai o endereço IP da saída
        ip_match = re.search(r'Endereço IP:\s+([\d\.]+)', ip_result.stdout)
        if not ip_match:
            print(f"Erro: Não foi possível obter o IP da interface {interface_name}.")
            exit(1)
            
        ip_address = ip_match.group(1)
        print(f"IP encontrado: {ip_address}")
        
        # Configurar DNS
        print(f"Configurando DNS para {ip_address} na interface {interface_name}...")
        subprocess.run(
            ['netsh', 'interface', 'ipv4', 'set', 'dns', 
             f'name="{interface_name}"', 'static', ip_address],
            check=True
        )
        
        # Desativar IPv6
        print(f"Desativando IPv6 na interface {interface_name}...")
        subprocess.run(
            ['netsh', 'interface', 'ipv6', 'set', 'interface', 
             f'interface="{interface_name}"', 'admin=disabled'],
            check=True
        )
        
        print("Script finalizado com sucesso.")
        
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar comando: {e}")
        exit(1)

if __name__ == "__main__":
    main()