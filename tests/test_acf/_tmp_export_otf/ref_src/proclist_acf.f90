module proclist_acf
use kind_values
use base, only: &
    update_accum_rate, &
    update_integ_rate, &
    determine_procsite, &
    update_clocks, &
    avail_sites, &
    null_species, &
    increment_procstat

use base_acf, only: &
    assign_particle_id, &
    update_id_arr, &
    update_displacement, &
    update_config_bin, &
    update_buffer_acf, &
    update_property_and_buffer_acf, &
    drain_process, &
    source_process, &
    update_kmc_step_acf, &
    get_kmc_step_acf, &
    update_trajectory, &
    update_displacement, &
    nr_of_annhilations, &
    wrap_count, &
    update_after_wrap_acf

use lattice

use proclist

implicit none


contains

subroutine do_kmc_steps_acf(n,traj_on)

!****f* proclist_acf/do_kmc_steps_acf
! FUNCTION
!    Performs ``n`` kMC step for the on the fly calculation of the autocorrelation function (ACF).
!    If one want to record the trajectory of the tracked species, it is possible to turn this on 
!    and off with the boolean traj_on.
!    * first update clock
!    * then configuration sampling step
!    * then ACF sampling step
!    * then tracking process
!    * then execute process
!    * last recording of trajectory(optional)
!      
! ARGUMENTS
!
!    ``n`` : Number of steps to run
!    ``traj_on`` : boolean, turn the recording of trajectory on and off
!******
    integer(kind=ilong), intent(in) :: n
    logical, intent(in) :: traj_on
    integer(kind=ilong) :: i, kmc_step_acf
    real(kind=rsingle) :: ran_proc, ran_time, ran_site
    integer(kind=iint) :: nr_site, proc_nr, particle, init_site, fin_site

    if (traj_on .eqv. .True.) then
        do i = 1, n
        call random_number(ran_time)
        call random_number(ran_proc)
        call random_number(ran_site)

        call update_accum_rate
        call update_clocks(ran_time)
        call update_kmc_step_acf()

        call update_integ_rate
        call determine_procsite(ran_proc, ran_site, proc_nr, nr_site)
        call update_config_bin()
        call get_diff_sites_acf(proc_nr, nr_site, init_site, fin_site)
        call assign_particle_id(init_site, particle)
        call update_id_arr(particle,init_site, fin_site)
        call update_after_wrap_acf
        call run_proc_nr(proc_nr, nr_site)
        call update_buffer_acf(particle)
        call get_kmc_step_acf(kmc_step_acf)
        call update_trajectory(particle,kmc_step_acf)
        enddo
        print *, "Number of annhilations", nr_of_annhilations
        print *, "Number of wraps", wrap_count
        if(nr_of_annhilations/wrap_count.ge.1 )then
            print *, "Number of kmc steps was too small for a good statistic of the ACF!"
        endif

    else
        do i = 1, n
        call random_number(ran_time)
        call random_number(ran_proc)
        call random_number(ran_site)
        call update_accum_rate
        call update_clocks(ran_time)

        call update_integ_rate
        call determine_procsite(ran_proc, ran_site, proc_nr, nr_site)
        call update_config_bin()
        call get_diff_sites_acf(proc_nr, nr_site, init_site, fin_site)
        call assign_particle_id(init_site, particle)
        call update_id_arr(particle,init_site, fin_site)
        call update_after_wrap_acf
        call run_proc_nr(proc_nr, nr_site)
        call update_buffer_acf(particle)
        enddo
        print *, "Number of annhilations", nr_of_annhilations
        print *, "Number of wraps", wrap_count
        if(nr_of_annhilations/wrap_count.ge.1 )then
            print *, "Number of kmc steps was too small for a good statistic of the ACF!"
        endif

    endif

end subroutine do_kmc_steps_acf

subroutine do_kmc_step_acf()

!****f* proclist_acf/do_kmc_step_acf
! FUNCTION
!    Performs exactly one kMC step for the on the fly calculation of the autocorrelation function (ACF).
!    * first update clock
!    * then configuration sampling step
!    * then ACF sampling step
!    * then tracking process
!    * last execute process
!
! ARGUMENTS
!
!    ``none``
!******
    real(kind=rsingle) :: ran_proc, ran_time, ran_site
    integer(kind=iint) :: nr_site, proc_nr, particle, init_site, fin_site

    call random_number(ran_time)
    call random_number(ran_proc)
    call random_number(ran_site)
    call update_accum_rate
    call update_clocks(ran_time)

    call update_integ_rate
    call determine_procsite(ran_proc, ran_site, proc_nr, nr_site)
    call update_config_bin()
    call get_diff_sites_acf(proc_nr, nr_site, init_site, fin_site)
    call assign_particle_id(init_site, particle)
    call update_id_arr(particle,init_site, fin_site)
    call update_after_wrap_acf
    call run_proc_nr(proc_nr, nr_site)
    call update_buffer_acf(particle)
end subroutine do_kmc_step_acf

subroutine do_kmc_steps_displacement(n,traj_on)

!****f* proclist_acf/do_kmc_displacement
! FUNCTION
!    Performs ``n`` kMC step for the calculation of mean squared displacement.
!    If one want to record the trajectory of the tracked species, it is possible to turn this on 
!    and off with the boolean traj_on.
!    * first update clock
!    * then configuration sampling step
!    * then tracking process
!    * then updating displacment
!    * then execute process
!    * last recording of trajectory(optional)
!
! ARGUMENTS
!
!    ``n`` : Number of steps to run
!    ``traj_on`` : boolean, turn the recording of trajectory on and off
!******
    integer(kind=ilong), intent(in) :: n
    logical, intent(in) :: traj_on
    integer(kind=ilong) :: i, kmc_step_acf
    real(kind=rsingle) :: ran_proc, ran_time, ran_site
    integer(kind=iint) :: nr_site, proc_nr, particle, init_site, fin_site
    real(kind=rdouble), dimension(3) :: displace_coord

    if (traj_on .eqv. .True.) then
        do i = 1, n
        call random_number(ran_time)
        call random_number(ran_proc)
        call random_number(ran_site)

        call update_accum_rate
        call update_clocks(ran_time)
        call update_kmc_step_acf()

        call update_integ_rate
        call determine_procsite(ran_proc, ran_site, proc_nr, nr_site)
        call get_diff_sites_displacement(proc_nr, nr_site, init_site, fin_site,displace_coord)
        call assign_particle_id(init_site, particle)
        call update_displacement(particle,displace_coord)
        call update_id_arr(particle,init_site, fin_site)
        call run_proc_nr(proc_nr, nr_site)
        call get_kmc_step_acf(kmc_step_acf)
        call update_trajectory(particle,kmc_step_acf)
        enddo

    else
        do i = 1, n
        call random_number(ran_time)
        call random_number(ran_proc)
        call random_number(ran_site)
        call update_accum_rate
        call update_clocks(ran_time)

        call update_integ_rate
        call determine_procsite(ran_proc, ran_site, proc_nr, nr_site)
        call get_diff_sites_displacement(proc_nr, nr_site, init_site, fin_site,displace_coord)
        call assign_particle_id(init_site, particle)
        call update_displacement(particle,displace_coord)
        call update_id_arr(particle,init_site, fin_site)
        call run_proc_nr(proc_nr, nr_site)
        enddo
    endif

end subroutine do_kmc_steps_displacement

subroutine do_kmc_step_displacement()

!****f* proclist_acf/do_kmc_step_displacement
! FUNCTION
!    Performs exactly one kMC step for the calculation of mean squared displacement.
!    * first update clock
!    * then configuration sampling step
!    * then tracking process
!    * then updating displacement
!    * last execute process
!
! ARGUMENTS
!
!    ``none``

    real(kind=rsingle) :: ran_proc, ran_time, ran_site
    integer(kind=iint) :: nr_site, proc_nr, particle, init_site, fin_site
    real(kind=rdouble), dimension(3) :: displace_coord
    call random_number(ran_time)
    call random_number(ran_proc)
    call random_number(ran_site)
    call update_accum_rate
    call update_clocks(ran_time)

    call update_integ_rate
    call determine_procsite(ran_proc, ran_site, proc_nr, nr_site)
    call get_diff_sites_displacement(proc_nr, nr_site, init_site,fin_site,displace_coord)
    call assign_particle_id(init_site, particle)
    call update_displacement(particle,displace_coord)
    call update_id_arr(particle,init_site, fin_site)
    call run_proc_nr(proc_nr, nr_site)
 
end subroutine do_kmc_step_displacement

subroutine get_diff_sites_acf(proc,nr_site,init_site,fin_site)

!****f* proclist_acf/get_diff_sites_acf
! FUNCTION
!    get_diff_sites_acf gives the site ``init_site``, which is occupied by the particle before the diffusion process 
!    and also the site ``fin_site`` after the diffusion process.
!
! ARGUMENTS
!
!    * ``proc`` integer representing the process number
!    * ``nr_site``  integer representing the site
!    * ``init_site`` integer representing the site, which is occupied by the particle before the diffusion process takes place
!    * ``fin_site`` integer representing the site, which is occupied by the particle after the diffusion process
!******
    integer(kind=iint), intent(in) :: proc
    integer(kind=iint), intent(in) :: nr_site
    integer(kind=iint), intent(out) :: init_site, fin_site

    integer(kind=iint), dimension(4) :: lsite
    integer(kind=iint), dimension(4) :: lsite_new
    integer(kind=iint), dimension(4) :: lsite_old
    integer(kind=iint) :: exit_site, entry_site

    lsite = nr2lattice(nr_site, :) + (/0,0,0,-1/)

    select case(proc)
    case(a_1_a_2)
        lsite_old = lsite + (/0, 0, 0, default_a_1/)
        init_site = lattice2nr(lsite_old(1),lsite_old(2),lsite_old(3),lsite_old(4))
        lsite_new = lsite + (/0, 0, 0, default_a_2/)
        fin_site = lattice2nr(lsite_new(1),lsite_new(2),lsite_new(3),lsite_new(4))

    case(a_1_b_1)
        lsite_old = lsite + (/0, 0, 0, default_a_1/)
        init_site = lattice2nr(lsite_old(1),lsite_old(2),lsite_old(3),lsite_old(4))
        lsite_new = lsite + (/0, 0, 0, default_b_1/)
        fin_site = lattice2nr(lsite_new(1),lsite_new(2),lsite_new(3),lsite_new(4))

    case(a_1_b_2)
        lsite_old = lsite + (/0, 0, 0, default_a_1/)
        init_site = lattice2nr(lsite_old(1),lsite_old(2),lsite_old(3),lsite_old(4))
        lsite_new = lsite + (/0, 0, 0, default_b_2/)
        fin_site = lattice2nr(lsite_new(1),lsite_new(2),lsite_new(3),lsite_new(4))

    case(a_2_a_1)
        lsite_new = lsite + (/0, 0, 0, default_a_1/)
        fin_site = lattice2nr(lsite_new(1),lsite_new(2),lsite_new(3),lsite_new(4))
        lsite_old = lsite + (/0, 0, 0, default_a_2/)
        init_site = lattice2nr(lsite_old(1),lsite_old(2),lsite_old(3),lsite_old(4))

    case(a_2_b_1)
        lsite_old = lsite + (/0, 0, 0, default_a_2/)
        init_site = lattice2nr(lsite_old(1),lsite_old(2),lsite_old(3),lsite_old(4))
        lsite_new = lsite + (/0, 0, 0, default_b_1/)
        fin_site = lattice2nr(lsite_new(1),lsite_new(2),lsite_new(3),lsite_new(4))

    case(a_2_b_2)
        lsite_old = lsite + (/0, 0, 0, default_a_2/)
        init_site = lattice2nr(lsite_old(1),lsite_old(2),lsite_old(3),lsite_old(4))
        lsite_new = lsite + (/0, 0, 0, default_b_2/)
        fin_site = lattice2nr(lsite_new(1),lsite_new(2),lsite_new(3),lsite_new(4))

    case(b_1_a_1)
        lsite_new = lsite + (/0, 0, 0, default_a_1/)
        fin_site = lattice2nr(lsite_new(1),lsite_new(2),lsite_new(3),lsite_new(4))
        lsite_old = lsite + (/0, 0, 0, default_b_1/)
        init_site = lattice2nr(lsite_old(1),lsite_old(2),lsite_old(3),lsite_old(4))

    case(b_1_a_2)
        lsite_new = lsite + (/0, 0, 0, default_a_2/)
        fin_site = lattice2nr(lsite_new(1),lsite_new(2),lsite_new(3),lsite_new(4))
        lsite_old = lsite + (/0, 0, 0, default_b_1/)
        init_site = lattice2nr(lsite_old(1),lsite_old(2),lsite_old(3),lsite_old(4))

    case(b_1_b_2)
        lsite_old = lsite + (/0, 0, 0, default_b_1/)
        init_site = lattice2nr(lsite_old(1),lsite_old(2),lsite_old(3),lsite_old(4))
        lsite_new = lsite + (/0, 0, 0, default_b_2/)
        fin_site = lattice2nr(lsite_new(1),lsite_new(2),lsite_new(3),lsite_new(4))

    case(b_2_a_1)
        lsite_new = lsite + (/0, 0, 0, default_a_1/)
        fin_site = lattice2nr(lsite_new(1),lsite_new(2),lsite_new(3),lsite_new(4))
        lsite_old = lsite + (/0, 0, 0, default_b_2/)
        init_site = lattice2nr(lsite_old(1),lsite_old(2),lsite_old(3),lsite_old(4))

    case(b_2_a_2)
        lsite_new = lsite + (/0, 0, 0, default_a_2/)
        fin_site = lattice2nr(lsite_new(1),lsite_new(2),lsite_new(3),lsite_new(4))
        lsite_old = lsite + (/0, 0, 0, default_b_2/)
        init_site = lattice2nr(lsite_old(1),lsite_old(2),lsite_old(3),lsite_old(4))

    case(b_2_b_1)
        lsite_new = lsite + (/0, 0, 0, default_b_1/)
        fin_site = lattice2nr(lsite_new(1),lsite_new(2),lsite_new(3),lsite_new(4))
        lsite_old = lsite + (/0, 0, 0, default_b_2/)
        init_site = lattice2nr(lsite_old(1),lsite_old(2),lsite_old(3),lsite_old(4))

    end select

end subroutine get_diff_sites_acf

subroutine get_diff_sites_displacement(proc,nr_site,init_site,fin_site,displace_coord)

!****f* proclist_acf/get_diff_sites_displacement
! FUNCTION
!    get_diff_sites_displacement gives the site ``init_site``, which is occupied by the particle before the diffusion process 
!    and also the site ``fin_site`` after the diffusion process.
!    Additionally, the displacement of the jumping particle will be saved.
!
! ARGUMENTS
!
!    * ``proc`` integer representing the process number
!    * ``nr_site``  integer representing the site
!    * ``init_site`` integer representing the site, which is occupied by the particle before the diffusion process takes place
!    * ``fin_site`` integer representing the site, which is occupied by the particle after the diffusion process
!    * ``displace_coord`` writeable 3 dimensional array, in which the displacement of the jumping particle will be stored.
!******
    integer(kind=iint), intent(in) :: proc
    integer(kind=iint), intent(in) :: nr_site
    integer(kind=iint), intent(out) :: init_site, fin_site

    integer(kind=iint), dimension(4) :: lsite
    integer(kind=iint), dimension(4) :: lsite_new
    integer(kind=iint), dimension(4) :: lsite_old
    integer(kind=iint) :: exit_site, entry_site
    real(kind=rdouble), dimension(3), intent(out) :: displace_coord

    lsite = nr2lattice(nr_site, :) + (/0,0,0,-1/)

    select case(proc)
    case(a_1_a_2)
        lsite_old = lsite + (/0, 0, 0, default_a_1/)
        init_site = lattice2nr(lsite_old(1),lsite_old(2),lsite_old(3),lsite_old(4))
        lsite_new = lsite + (/0, 0, 0, default_a_2/)
        fin_site = lattice2nr(lsite_new(1),lsite_new(2),lsite_new(3),lsite_new(4))
        displace_coord = matmul(unit_cell_size,(/(lsite_new(1)-lsite_old(1)),(lsite_new(2)-lsite_old(2)),(lsite_new(3)-lsite_old(3))/) + (site_positions(lsite_new(4),:) - site_positions(lsite_old(4),:)))

    case(a_1_b_1)
        lsite_old = lsite + (/0, 0, 0, default_a_1/)
        init_site = lattice2nr(lsite_old(1),lsite_old(2),lsite_old(3),lsite_old(4))
        lsite_new = lsite + (/0, 0, 0, default_b_1/)
        fin_site = lattice2nr(lsite_new(1),lsite_new(2),lsite_new(3),lsite_new(4))
        displace_coord = matmul(unit_cell_size,(/(lsite_new(1)-lsite_old(1)),(lsite_new(2)-lsite_old(2)),(lsite_new(3)-lsite_old(3))/) + (site_positions(lsite_new(4),:) - site_positions(lsite_old(4),:)))

    case(a_1_b_2)
        lsite_old = lsite + (/0, 0, 0, default_a_1/)
        init_site = lattice2nr(lsite_old(1),lsite_old(2),lsite_old(3),lsite_old(4))
        lsite_new = lsite + (/0, 0, 0, default_b_2/)
        fin_site = lattice2nr(lsite_new(1),lsite_new(2),lsite_new(3),lsite_new(4))
        displace_coord = matmul(unit_cell_size,(/(lsite_new(1)-lsite_old(1)),(lsite_new(2)-lsite_old(2)),(lsite_new(3)-lsite_old(3))/) + (site_positions(lsite_new(4),:) - site_positions(lsite_old(4),:)))

    case(a_2_a_1)
        lsite_new = lsite + (/0, 0, 0, default_a_1/)
        fin_site = lattice2nr(lsite_new(1),lsite_new(2),lsite_new(3),lsite_new(4))
        lsite_old = lsite + (/0, 0, 0, default_a_2/)
        init_site = lattice2nr(lsite_old(1),lsite_old(2),lsite_old(3),lsite_old(4))
        displace_coord = matmul(unit_cell_size,(/(lsite_new(1)-lsite_old(1)),(lsite_new(2)-lsite_old(2)),(lsite_new(3)-lsite_old(3))/) + (site_positions(lsite_new(4),:) - site_positions(lsite_old(4),:)))

    case(a_2_b_1)
        lsite_old = lsite + (/0, 0, 0, default_a_2/)
        init_site = lattice2nr(lsite_old(1),lsite_old(2),lsite_old(3),lsite_old(4))
        lsite_new = lsite + (/0, 0, 0, default_b_1/)
        fin_site = lattice2nr(lsite_new(1),lsite_new(2),lsite_new(3),lsite_new(4))
        displace_coord = matmul(unit_cell_size,(/(lsite_new(1)-lsite_old(1)),(lsite_new(2)-lsite_old(2)),(lsite_new(3)-lsite_old(3))/) + (site_positions(lsite_new(4),:) - site_positions(lsite_old(4),:)))

    case(a_2_b_2)
        lsite_old = lsite + (/0, 0, 0, default_a_2/)
        init_site = lattice2nr(lsite_old(1),lsite_old(2),lsite_old(3),lsite_old(4))
        lsite_new = lsite + (/0, 0, 0, default_b_2/)
        fin_site = lattice2nr(lsite_new(1),lsite_new(2),lsite_new(3),lsite_new(4))
        displace_coord = matmul(unit_cell_size,(/(lsite_new(1)-lsite_old(1)),(lsite_new(2)-lsite_old(2)),(lsite_new(3)-lsite_old(3))/) + (site_positions(lsite_new(4),:) - site_positions(lsite_old(4),:)))

    case(b_1_a_1)
        lsite_new = lsite + (/0, 0, 0, default_a_1/)
        fin_site = lattice2nr(lsite_new(1),lsite_new(2),lsite_new(3),lsite_new(4))
        lsite_old = lsite + (/0, 0, 0, default_b_1/)
        init_site = lattice2nr(lsite_old(1),lsite_old(2),lsite_old(3),lsite_old(4))
        displace_coord = matmul(unit_cell_size,(/(lsite_new(1)-lsite_old(1)),(lsite_new(2)-lsite_old(2)),(lsite_new(3)-lsite_old(3))/) + (site_positions(lsite_new(4),:) - site_positions(lsite_old(4),:)))

    case(b_1_a_2)
        lsite_new = lsite + (/0, 0, 0, default_a_2/)
        fin_site = lattice2nr(lsite_new(1),lsite_new(2),lsite_new(3),lsite_new(4))
        lsite_old = lsite + (/0, 0, 0, default_b_1/)
        init_site = lattice2nr(lsite_old(1),lsite_old(2),lsite_old(3),lsite_old(4))
        displace_coord = matmul(unit_cell_size,(/(lsite_new(1)-lsite_old(1)),(lsite_new(2)-lsite_old(2)),(lsite_new(3)-lsite_old(3))/) + (site_positions(lsite_new(4),:) - site_positions(lsite_old(4),:)))

    case(b_1_b_2)
        lsite_old = lsite + (/0, 0, 0, default_b_1/)
        init_site = lattice2nr(lsite_old(1),lsite_old(2),lsite_old(3),lsite_old(4))
        lsite_new = lsite + (/0, 0, 0, default_b_2/)
        fin_site = lattice2nr(lsite_new(1),lsite_new(2),lsite_new(3),lsite_new(4))
        displace_coord = matmul(unit_cell_size,(/(lsite_new(1)-lsite_old(1)),(lsite_new(2)-lsite_old(2)),(lsite_new(3)-lsite_old(3))/) + (site_positions(lsite_new(4),:) - site_positions(lsite_old(4),:)))

    case(b_2_a_1)
        lsite_new = lsite + (/0, 0, 0, default_a_1/)
        fin_site = lattice2nr(lsite_new(1),lsite_new(2),lsite_new(3),lsite_new(4))
        lsite_old = lsite + (/0, 0, 0, default_b_2/)
        init_site = lattice2nr(lsite_old(1),lsite_old(2),lsite_old(3),lsite_old(4))
        displace_coord = matmul(unit_cell_size,(/(lsite_new(1)-lsite_old(1)),(lsite_new(2)-lsite_old(2)),(lsite_new(3)-lsite_old(3))/) + (site_positions(lsite_new(4),:) - site_positions(lsite_old(4),:)))

    case(b_2_a_2)
        lsite_new = lsite + (/0, 0, 0, default_a_2/)
        fin_site = lattice2nr(lsite_new(1),lsite_new(2),lsite_new(3),lsite_new(4))
        lsite_old = lsite + (/0, 0, 0, default_b_2/)
        init_site = lattice2nr(lsite_old(1),lsite_old(2),lsite_old(3),lsite_old(4))
        displace_coord = matmul(unit_cell_size,(/(lsite_new(1)-lsite_old(1)),(lsite_new(2)-lsite_old(2)),(lsite_new(3)-lsite_old(3))/) + (site_positions(lsite_new(4),:) - site_positions(lsite_old(4),:)))

    case(b_2_b_1)
        lsite_new = lsite + (/0, 0, 0, default_b_1/)
        fin_site = lattice2nr(lsite_new(1),lsite_new(2),lsite_new(3),lsite_new(4))
        lsite_old = lsite + (/0, 0, 0, default_b_2/)
        init_site = lattice2nr(lsite_old(1),lsite_old(2),lsite_old(3),lsite_old(4))
        displace_coord = matmul(unit_cell_size,(/(lsite_new(1)-lsite_old(1)),(lsite_new(2)-lsite_old(2)),(lsite_new(3)-lsite_old(3))/) + (site_positions(lsite_new(4),:) - site_positions(lsite_old(4),:)))

    end select

end subroutine get_diff_sites_displacement

end module proclist_acf
